# mv44_all_in_one.py

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject, TextStringObject, BooleanObject, DictionaryObject
)
import urllib.request
import webbrowser
import os
import re
import kevinlulee as kx  # kx.readfile / writefile / cpfile / mvfile / rmdir / pprint


# -------------------------
# Path + IO helpers
# -------------------------

def expand_path(p: str) -> str:
    return os.path.abspath(os.path.expanduser(os.path.expandvars(p)))

def fetch_pdf_bytes(src: str) -> bytes:
    if src.lower().startswith(("http://", "https://")):
        with urllib.request.urlopen(src) as r:
            return r.read()
    path = expand_path(src)
    with open(path, "rb") as fh:
        return fh.read()


# -------------------------
# Normalization helpers
# -------------------------

def _norm_key(s: str) -> str:
    s0 = s.replace("\u00a0", " ")
    s1 = re.sub(r"[^A-Za-z0-9]+", "_", s0)
    s2 = re.sub(r"_+", "_", s1).strip("_")
    return s2.lower()

def _snake(s: str) -> str:
    return _norm_key(s)

def _strip_pdf_name(n) -> str:
    s = str(n)
    return s[1:] if s.startswith("/") else s

def _canonize_label(raw_name: str) -> str:
    label = raw_name.strip()
    label = label.replace("FULL ", "")
    label = label.replace("IDENTIFICATION INFORMATION", "Identification")
    return _snake(label)

def _dedupe(base: str, used: set) -> str:
    if base not in used:
        used.add(base)
        return base
    i = 2
    while True:
        cand = f"{base}_{i}"
        if cand not in used:
            used.add(cand)
            return cand
        i += 1

def _booly(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("1", "t", "true", "y", "yes", "on", "checked")

def _maybe_date_mmddyyyy(s: str) -> str:
    s2 = str(s).strip()
    if "-" in s2:
        parts = s2.split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            y, m, d = parts
            return f"{int(m):02d}/{int(d):02d}/{y}"
    if "/" in s2:
        parts = s2.split("/")
        if len(parts) == 3:
            m, d, y = parts
            if len(y) == 2:
                y = f"20{y}"
            return f"{int(m):02d}/{int(d):02d}/{int(y):04d}"
    return s2

def _clean_phone(s: str) -> str:
    digits = re.sub(r"[^0-9]", "", str(s))
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
    return digits

def _clean_zip(s: str) -> str:
    digits = re.sub(r"[^0-9]", "", str(s))
    return digits[:5] if len(digits) >= 5 else digits

def _coerce_choice(v: Any, options: List[str]) -> str:
    if isinstance(v, str):
        s = v.strip()
        for opt in options:
            if s.lower() == opt.lower():
                return opt
        for opt in options:
            if len(s) <= 3 and opt.lower().startswith(s.lower()):
                return opt
    if isinstance(v, int):
        if 0 <= v < len(options):
            return options[v]
    return options[0] if options else str(v)


# -------------------------
# PDF field model
# -------------------------

@dataclass
class Field:
    pdf_name: str
    page_index: int
    field_type: str            # "text" | "checkbox" | "radio" | "choice" | "signature"
    options: List[str]         # for radio/choice; for checkbox, states excluding Off
    canonical_key: str
    raw_name: str

@dataclass
class Schema:
    fields: List[Field]
    canonical_to_pdf: Dict[str, str]
    sample: Dict[str, Any]
    aliases: Dict[str, str]    # alias_key -> canonical_key


# -------------------------
# PDF low-level helpers
# -------------------------

def _pdf_name_to_str(n) -> str:
    s = str(n)
    return s[1:] if s.startswith("/") else s

def _anno_field_name(annot) -> str:
    if "/T" in annot:
        return str(annot["/T"])
    if "/Parent" in annot and "/T" in annot["/Parent"]:
        return str(annot["/Parent"]["/T"])
    return "unnamed"

def _anno_parent(annot):
    return annot["/Parent"] if "/Parent" in annot else annot

def _widget_options(annot) -> List[str]:
    opts = []
    if "/AP" in annot and "/N" in annot["/AP"]:
        apn = annot["/AP"]["/N"]
        for k in apn.keys():
            key = _pdf_name_to_str(k)
            if key.lower() != "off":
                opts.append(key)
    return opts

def _ensure_acroform_resources(writer: PdfWriter):
    root = writer._root_object
    if NameObject("/AcroForm") not in root:
        root.update({ NameObject("/AcroForm"): DictionaryObject() })
    acro = root[NameObject("/AcroForm")]
    # Default appearance & resources so viewers render text
    acro.update({
        NameObject("/NeedAppearances"): BooleanObject(True),
        NameObject("/DA"): TextStringObject("/Helv 0 Tf 0 g"),
        NameObject("/DR"): DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/Helv"): DictionaryObject({
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                })
            })
        })
    })
    if NameObject("/XFA") in acro:
        acro.pop(NameObject("/XFA"))


# -------------------------
# Schema extraction (gets every widget)
# -------------------------

def extract_mv44_schema(pdf_bytes: bytes) -> Schema:
    reader = PdfReader(BytesIO(pdf_bytes))
    fields: List[Field] = []
    seen_names = set()

    for pi, page in enumerate(reader.pages):
        if "/Annots" not in page:
            continue
        for ref in page["/Annots"]:
            annot = ref.get_object()
            if annot.get("/Subtype") != NameObject("/Widget"):
                continue

            raw_name = _anno_field_name(annot)
            field_dict = _anno_parent(annot)
            ft = str(field_dict.get("/FT", ""))  # /Tx, /Btn, /Ch, /Sig

            # options via appearances; for /Ch check /Opt as well
            opt_states: List[str] = _widget_options(annot)
            if ft == "/Ch" and "/Opt" in field_dict:
                text_opts = [str(o) for o in field_dict["/Opt"]]
                if len(text_opts) > 0:
                    opt_states = text_opts

            if ft == "/Tx":
                ftype = "text"
            elif ft == "/Sig":
                ftype = "signature"
            elif ft == "/Ch":
                ftype = "choice"
            elif ft == "/Btn":
                ftype = "radio" if len(opt_states) > 1 else "checkbox"
            else:
                ftype = "text"

            canon_key = _dedupe(_canonize_label(raw_name), seen_names)

            fields.append(Field(
                pdf_name=raw_name,
                page_index=pi,
                field_type=ftype,
                options=opt_states,
                canonical_key=canon_key,
                raw_name=raw_name
            ))

    canonical_to_pdf = {f.canonical_key: f.pdf_name for f in fields}

    # sample placeholders
    sample: Dict[str, Any] = {}
    for f in fields:
        lk = f.canonical_key
        if f.field_type == "text":
            v = ""
            if "dob" in lk or "date_of_birth" in lk or lk.endswith("_dob"):
                v = "01/01/2000"
            elif lk.endswith("_date") or lk.startswith("date_"):
                v = "01/01/2025"
            elif "telephone" in lk or "phone" in lk:
                v = "(555) 555-5555"
            elif lk.endswith("_zip") or lk.endswith("_zip_code") or lk.endswith("_zipcode"):
                v = "10001"
            elif "eye_color" in lk:
                v = "Brown"
            elif lk in ("sex", "gender"):
                v = "M"
            elif "height" in lk and "feet" in lk:
                v = "5"
            elif "height" in lk and "inch" in lk:
                v = "8"
            elif "ssn" in lk:
                v = "123-45-6789"
            sample[lk] = v
        elif f.field_type == "checkbox":
            sample[lk] = False
        elif f.field_type in ("radio", "choice"):
            sample[lk] = f.options[0] if f.options else ""
        elif f.field_type == "signature":
            sample[lk] = ""

    # broad alias map (auto-derived from labels)
    aliases: Dict[str, str] = {}
    def add_alias(alias: str, canonical: str):
        aliases[_snake(alias)] = canonical

    for f in fields:
        ck = f.canonical_key
        label = f.raw_name.upper()

        if "FIRST" in label:
            add_alias("first_name", ck); add_alias("fname", ck); add_alias("given_name", ck); add_alias("first", ck)
        if "MIDDLE" in label:
            add_alias("middle_name", ck); add_alias("mname", ck); add_alias("mi", ck)
        if "LAST" in label:
            add_alias("last_name", ck); add_alias("lname", ck); add_alias("surname", ck); add_alias("family_name", ck); add_alias("last", ck)
        if "SUFFIX" in label:
            add_alias("suffix", ck)

        if "DATE OF BIRTH" in label or "DOB" in label:
            add_alias("dob", ck); add_alias("birthdate", ck); add_alias("date_of_birth", ck)

        if "SEX" in label or "GENDER" in label:
            add_alias("sex", ck); add_alias("gender", ck); add_alias("male_female_x", ck)

        if "HEIGHT" in label and "FEET" in label:
            add_alias("height_ft", ck); add_alias("height_feet", ck)
        if "HEIGHT" in label and "INCH" in label:
            add_alias("height_in", ck); add_alias("height_inches", ck)
        if "WEIGHT" in label:
            add_alias("weight", ck); add_alias("weight_lbs", ck)

        if "EYE COLOR" in label or "EYE" in label:
            add_alias("eye_color", ck); add_alias("eyes", ck)

        if "TELEPHONE" in label or "PHONE" in label:
            add_alias("phone", ck); add_alias("mobile", ck); add_alias("cell", ck); add_alias("telephone", ck)

        if "SOCIAL SECURITY" in label or "SSN" in label:
            add_alias("ssn", ck); add_alias("social_security_number", ck); add_alias("social", ck); add_alias("ssn_full", ck); add_alias("ssn_last4", ck)

        if "ADDRESS WHERE YOU GET YOUR MAIL" in label or "MAILING" in label:
            if "APT" in label:
                add_alias("mailing_apt", ck); add_alias("mail_apt", ck); add_alias("apt", ck)
            elif "CITY" in label:
                add_alias("mailing_city", ck); add_alias("mail_city", ck)
            elif "STATE" in label:
                add_alias("mailing_state", ck); add_alias("mail_state", ck)
            elif "ZIP" in label:
                add_alias("mailing_zip", ck); add_alias("mail_zip", ck); add_alias("mail_zipcode", ck)
            elif "COUNTY" in label:
                add_alias("mailing_county", ck); add_alias("mail_county", ck)
            else:
                add_alias("mailing_street", ck); add_alias("mail_street", ck); add_alias("mail_address1", ck); add_alias("mail_address", ck)

        if "ADDRESS WHERE YOU LIVE" in label or "RESIDENCE" in label:
            if "APT" in label:
                add_alias("residence_apt", ck); add_alias("physical_apt", ck)
            elif "CITY" in label:
                add_alias("residence_city", ck); add_alias("physical_city", ck)
            elif "STATE" in label:
                add_alias("residence_state", ck); add_alias("physical_state", ck)
            elif "ZIP" in label:
                add_alias("residence_zip", ck); add_alias("physical_zip", ck)
            elif "COUNTY" in label:
                add_alias("residence_county", ck); add_alias("physical_county", ck)
            else:
                add_alias("residence_street", ck); add_alias("physical_street", ck); add_alias("residential_address", ck)

        if "APPLYING FOR" in label or "PURPOSE FOR APPLICATION" in label:
            add_alias("application_purpose", ck); add_alias("purpose", ck); add_alias("applying_for", ck)
        if "VETERAN" in label:
            add_alias("veteran", ck); add_alias("veteran_printed", ck)
        if "DONATE LIFE" in label or "ORGAN" in label:
            add_alias("organ_donor", ck); add_alias("donate_life_enroll", ck); add_alias("donor_consent", ck); add_alias("donor_donation_1usd", ck)
        if "VOTER" in label or "BOARD OF ELECTIONS" in label:
            add_alias("voter_register", ck); add_alias("voter_yesno", ck)
        if "SELECTIVE SERVICE" in label:
            add_alias("selective_service_no", ck); add_alias("sss_no", ck)

        if "COMMERCIAL DRIVER LICENSE APPLICANTS ONLY" in label:
            add_alias("cdl_section_ack", ck)
        if "Non-excepted Interstate" in label or "driving types" in label or "Excepted" in label:
            add_alias("cdl_driving_type", ck); add_alias("cdl_type", ck)
        if "In the past 10 years" in label and "another state" in label:
            add_alias("cdl_past_10_years_other_state_licenses", ck)
        if "Has your driver license, learner permit, or privilege" in label:
            add_alias("license_suspended_revoked_cancelled", ck)
        if "Do you need a hearing aid" in label:
            add_alias("needs_hearing_aid_or_full_view_mirror", ck)
        if "Have you lost the use of a leg, arm, hand or eye" in label:
            add_alias("lost_use_of_limb_or_eye", ck)

    return Schema(
        fields=fields,
        canonical_to_pdf=canonical_to_pdf,
        sample=sample,
        aliases=aliases
    )


# -------------------------
# Merge + coerce user input
# -------------------------

def merge_user_input(schema: Schema, user_input: Dict[str, Any]) -> Dict[str, Any]:
    canonical = dict(schema.sample)

    # detect split height fields and allow compact "height"
    height_ft_keys = [k for k in canonical.keys() if "height" in k and "feet" in k]
    height_in_keys = [k for k in canonical.keys() if "height" in k and "inch" in k]

    def to_canonical_key(k: str) -> Optional[str]:
        nk = _snake(k)
        if nk in schema.aliases:
            return schema.aliases[nk]
        if nk in canonical:
            return nk
        return None

    # expand compact height if present
    keys_norm = { _snake(x): x for x in user_input.keys() }
    if "height" in keys_norm and len(height_ft_keys) == 1 and len(height_in_keys) == 1:
        h_raw = str(user_input[keys_norm["height"]])
        m = re.findall(r"[0-9]+", h_raw)
        if len(m) >= 1:
            canonical[height_ft_keys[0]] = str(int(m[0]))
        if len(m) >= 2:
            canonical[height_in_keys[0]] = str(int(m[1]))

    for k, v in user_input.items():
        ckey = to_canonical_key(k)
        if ckey is None:
            continue
        fmeta = next((f for f in schema.fields if f.canonical_key == ckey), None)
        if fmeta is None:
            continue

        if fmeta.field_type == "checkbox":
            canonical[ckey] = _booly(v)
        elif fmeta.field_type in ("radio", "choice"):
            canonical[ckey] = _coerce_choice(v, fmeta.options)
        elif fmeta.field_type == "text":
            lk = ckey
            sv = str(v)
            if "date" in lk or "dob" in lk:
                canonical[ckey] = _maybe_date_mmddyyyy(sv)
            elif "phone" in lk or "telephone" in lk:
                canonical[ckey] = _clean_phone(sv)
            elif lk.endswith("_zip") or lk.endswith("_zip_code") or lk.endswith("_zipcode"):
                canonical[ckey] = _clean_zip(sv)
            else:
                canonical[ckey] = sv
        elif fmeta.field_type == "signature":
            canonical[ckey] = str(v)

    return canonical


# -------------------------
# Robust filler: set /V and /AS, ensure /DA + /DR
# -------------------------

def fill_pdf_bytes(pdf_bytes: bytes, merged: Dict[str, Any], schema: Schema) -> bytes:
    reader = PdfReader(BytesIO(pdf_bytes))
    writer = PdfWriter()

    for p in reader.pages:
        writer.add_page(p)

    if "/AcroForm" in reader.trailer["/Root"]:
        writer._root_object.update({ NameObject("/AcroForm"): reader.trailer["/Root"]["/AcroForm"] })

    # index widgets
    widgets_by_name: Dict[str, List[Tuple[int, Any]]] = {}
    parent_by_name: Dict[str, Any] = {}
    options_by_name: Dict[str, List[str]] = {}

    for pi, page in enumerate(writer.pages):
        if "/Annots" not in page:
            continue
        for aref in page["/Annots"]:
            annot = aref.get_object()
            if annot.get("/Subtype") != NameObject("/Widget"):
                continue
            name = _anno_field_name(annot)
            field_dict = _anno_parent(annot)
            widgets_by_name.setdefault(name, []).append((pi, annot))
            parent_by_name[name] = field_dict
            if name not in options_by_name:
                options_by_name[name] = _widget_options(annot)

    _ensure_acroform_resources(writer)

    for canon_key, pdf_name in schema.canonical_to_pdf.items():
        if canon_key not in merged:
            continue
        if pdf_name not in parent_by_name:
            base = re.split(r"[\.:\[\]]+", pdf_name)[-1].strip()
            candidates = [k for k in parent_by_name.keys() if k.endswith(base)]
            if len(candidates) == 1:
                pdf_name = candidates[0]
            else:
                continue

        pdict = parent_by_name[pdf_name]
        widgets = [w for _, w in widgets_by_name[pdf_name]]
        opts = options_by_name.get(pdf_name, [])
        fmeta = next((f for f in schema.fields if f.pdf_name == pdf_name), None)
        value = merged[canon_key]

        if fmeta and fmeta.field_type == "text":
            pdict.update({ NameObject("/V"): TextStringObject(str(value)) })
        elif fmeta and fmeta.field_type == "choice":
            chosen = _coerce_choice(value, fmeta.options or opts)
            pdict.update({ NameObject("/V"): TextStringObject(chosen) })
        elif fmeta and fmeta.field_type == "checkbox":
            on_state = (fmeta.options or opts or ["Yes"])[0]
            for w in widgets:
                if _booly(value):
                    pdict.update({ NameObject("/V"): NameObject(f"/{on_state}") })
                    w.update({ NameObject("/AS"): NameObject(f"/{on_state}") })
                else:
                    pdict.update({ NameObject("/V"): NameObject("/Off") })
                    w.update({ NameObject("/AS"): NameObject("/Off") })
        elif fmeta and fmeta.field_type == "radio":
            chosen = _coerce_choice(value, fmeta.options or opts)
            pdict.update({ NameObject("/V"): NameObject(f"/{chosen}") })
            for w in widgets:
                wopts = _widget_options(w)
                if chosen in wopts:
                    w.update({ NameObject("/AS"): NameObject(f"/{chosen}") })
                else:
                    w.update({ NameObject("/AS"): NameObject("/Off") })
        else:
            pdict.update({ NameObject("/V"): TextStringObject(str(value)) })

    # write to bytes
    bio = BytesIO()
    writer.write(bio)
    return bio.getvalue()


# -------------------------
# High-level pipeline
# -------------------------
def write_bytes_to_pdf(output_filename, pdf_bytes):
    """
    Writes a given bytes object to a PDF file.

    Args:
        pdf_bytes (bytes): The byte data representing the PDF content.
        output_filename (str): The name of the output PDF file.
    """
    try:
        with open(output_filename, 'wb') as f:
            f.write(pdf_bytes)
        print(f"Successfully wrote bytes to {output_filename}")
    except IOError as e:
        print(f"Error writing to file: {e}")
def fill_mv44_pipeline(pdf_src: str, output_pdf_path: str, user_input: Dict[str, Any]) -> Dict[str, Any]:
    pdf_bytes = fetch_pdf_bytes(pdf_src)
    schema = extract_mv44_schema(pdf_bytes)
    merged = merge_user_input(schema, user_input)
    out_bytes = fill_pdf_bytes(pdf_bytes, merged, schema)

    out_path = expand_path(output_pdf_path)
    write_bytes_to_pdf(out_path, out_bytes)
    webbrowser.open(out_path)

    return {
        "output_pdf_path": out_path,
        "merged": merged,
        "aliases": schema.aliases,
        "canonical_to_pdf": schema.canonical_to_pdf,
        "field_count": len(schema.fields),
    }


# -------------------------
# Sample call (requested)
# -------------------------

if __name__ == "__main__":
    sample_user_input = {
        "first_name": "Kevin",
        "middle_name": "Lu",
        "last_name": "Lee",
        "sex": "M",
        "eye_color": "Brown",
        "weight": "165",
        "weight_lbs": "165",
        "height": "5 10",
        "height_ft": "5",
        "height_in": "10",

        # residence
        "residence_street": "1028 65th St",
        "residence_city": "Brooklyn",
        "residence_state": "NY",
        "residence_zip": "11219",
        "residence_county": "Kings",

        # mailing (same)
        "mailing_street": "1028 65th St",
        "mailing_city": "Brooklyn",
        "mailing_state": "NY",
        "mailing_zip": "11219",
        "mailing_county": "Kings",
    }

    result = fill_mv44_pipeline(
        pdf_src=kx.get_most_recent_file(kx.DLDIR),
        output_pdf_path="~/scratch/temp.pdf",
        user_input=sample_user_input,
    )
    # kx.pprint(result)



# 2025-09-15 aicmp: there are some problems. many fields are not filled out, also, the font is gray for the input parts. the font should be black. 
