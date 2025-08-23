FILETYPE_TO_EXT = {
    # base
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "text": "txt",

    # web frameworks & ecosystems
    "react": "jsx",
    "react-typescript": "tsx",
    "next": "tsx",
    "nextjs": "tsx",
    "remix": "tsx",
    "preact": "jsx",
    "solid": "tsx",
    "qwik": "tsx",
    "nuxt": "vue",
    "sveltekit": "svelte",
    "angular": "ts",
    "nest": "ts",
    "nestjs": "ts",
    "deno": "ts",
    "express": "js",
    "koa": "js",
    "hapi": "js",
    "sails": "js",
    "adonis": "ts",
    "react-native": "tsx",
    "gatsby": "jsx",
    "eleventy": "njk",
    "astrojs": "astro",
    "tailwind": "css",      # Tailwind source is CSS (plus config files)
    "webpack": "js",
    "vite": "ts",

    # python web frameworks
    "django": "py",
    "flask": "py",
    "fastapi": "py",

    # templating (non-identity only)
    "handlebars": "hbs",
    "nunjucks": "njk",
    "jinja": "j2",
    "jinja2": "j2",

    # css tooling (avoid identity like scss/sass/less)
    "postcss": "css",

    # databases & query languages
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "mariadb": "sql",
    "sqlite": "sql",        # query files; database files often use .sqlite/.db
    "duckdb": "sql",
    "redshift": "sql",
    "bigquery": "sql",
    "snowflake": "sql",
    "mssql": "sql",
    "tsql": "sql",
    "oracle": "sql",
    "plsql": "sql",
    "db2": "sql",
    "clickhouse": "sql",
    "trino": "sql",
    "presto": "sql",
    "timescaledb": "sql",
    "questdb": "sql",
    "cassandra": "cql",
    "neo4j": "cypher",
    "mongodb": "bson",      # dumps; shell scripts are often .js
    "dynamodb": "json",
    "elasticsearch": "json",
    "firestore": "json",
    "influxdb": "flux",

    # infra / config
    "graphql": "gql",
    "terraform": "tf",
    "starlark": "bzl",
    "dotenv": "env",
    "kubernetes": "yaml",
    "helm": "yaml",
    "cloudformation": "yaml",
    "ansible": "yaml",
    "openapi": "yaml",
    "nginx": "conf",
    "apache": "conf",

    # docs / markup
    "latex": "tex",
    "markdown": "md",
    "restructuredtext": "rst",
    "typst": "typ",
    "protobuf": "proto",

    # hardware / HDL
    "verilog": "v",
    "systemverilog": "sv",
    "vhdl": "vhd",
}

# 1) Filetypes → canonical extensions (duplicates removed)


# 2) Plain list of extension tokens (deduped, expanded)
EXT_TOKENS = [
    # code & scripting
    "py", "pyw", "js", "mjs", "jsx", "ts", "tsx", "sh", "bash", "ps1", "bat", "cmd",
    "rb", "php", "go", "java", "kt", "kts", "scala", "swift", "rs", "cs", "vb",
    "c", "cpp", "cc", "cxx", "c++", "h", "hpp", "r", "jl", "pl", "pm", "hs",
    "erl", "ex", "exs", "clj", "cljs", "edn", "dart", "lua", "m", "mm", "mat",
    "v", "sv", "vhd",

    # web & markup
    "html", "htm", "css", "xml", "json", "yml", "yaml", "ini", "toml", "cfg", "conf", "env",
    "md", "markdown", "mdown", "rst", "tex", "typ", "typst", "log",

    # notebooks, data & db
    "ipynb", "csv", "tsv", "sql", "sqlite", "db", "parquet", "feather", "avro", "orc", "yb", "br",

    # docs & presentations
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",

    # archives & packages
    "zip", "tar", "gz", "bz2", "xz", "7z", "rar",

    # images & vector
    "jpg", "jpeg", "jpe", "png", "gif", "bmp", "tif", "tiff", "svg", "webp", "ico", "heic",

    # audio
    "mp3", "wav", "flac", "m4a", "ogg", "aac", "wma",

    # video
    "mp4", "mkv", "webm", "mov", "avi", "m4v", "3gp",

    # fonts
    "ttf", "otf", "woff", "woff2", "eot",

    # 3D / CAD
    "obj", "fbx", "glb", "gltf", "stl",
]



EXTENSIONS = list(set(EXT_TOKENS + list(FILETYPE_TO_EXT.values())))
