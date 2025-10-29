from __future__ import annotations
import kevinlulee as kx

from datetime import datetime

def calculate_birth_year(birthday_month, birthday_day, current_age):
    """
    Calculate birth year from birthday and current age.
    
    Args:
        birthday_month (int): Month of birth (1-12)
        birthday_day (int): Day of birth (1-31)
        current_age (int): Current age
        
    Returns:
        tuple: (birth_year, birthday_date_string)
    """
    current_date = datetime.now()
    current_year = current_date.year
    
    # Calculate birth year
    birth_year = current_year - current_age
    
    # Check if birthday hasn't occurred yet this year
    birthday_this_year = datetime(current_year, birthday_month, birthday_day)
    if current_date < birthday_this_year:
        birth_year -= 1
    
    birthday_string = f"{birthday_month}/{birthday_day}/{birth_year}"
    
    return birth_year, birthday_string


# Example usage
if __name__ == "__main__.asdf":
    birth_year, birthday = calculate_birth_year(
        birthday_month=9,
        birthday_day=17,
        current_age=45
    )
    
    print(f"Birth year: {birth_year}")
    print(f"Birthday: {birthday}")


from datetime import datetime

def calculate_birth_year_from_grade(year, grade):
    """
    Calculate birth year from a statement like "in 2019 I was in 6th grade".
    
    Assumes:
    - School year runs from September to June
    - Student's age in a grade follows typical US progression (6th grade ≈ 11-12 years old)
    - Kindergarten starts at age 5-6
    
    Args:
        year (int): The year mentioned (e.g., 2019)
        grade (int or str): Grade level (e.g., 6, "6th", "K" for kindergarten)
        
    Returns:
        tuple: (birth_year, approximate_age_range)
    """
    # Convert grade to number
    if isinstance(grade, str):
        grade = grade.lower().strip()
        if grade in ['k', 'kindergarten']:
            grade = 0
        else:
            # Extract number from string like "6th"
            grade = int(''.join(filter(str.isdigit, grade)))
    
    # Calculate typical age during that grade
    # Kindergarten (grade 0): age 5-6
    # 1st grade: age 6-7
    # 6th grade: age 11-12, etc.
    typical_age = grade + 5  # Lower bound
    
    # Most of the school year happens in the stated year
    # (Sept 2019 - June 2020 is called "2019 school year")
    # So birth year = year - typical_age
    birth_year_early = year - typical_age - 1  # If birthday is Sept-Dec
    birth_year_late = year - typical_age         # If birthday is Jan-Aug
    
    current_year = datetime.now().year
    current_age_early = current_year - birth_year_late
    current_age_late = current_year - birth_year_early
    
    return (birth_year_early, birth_year_late, current_age_early, current_age_late)


# Example usage
if __name__ == "__main__.asdfjkhasdfjk":
    year = 2000
    grade = 5
    birth_years = calculate_birth_year_from_grade(year, grade)
    print(f"If you were in {kx.ordinal(grade)} grade in {year}:")
    print(f"Birth year range: {birth_years[0]}-{birth_years[1]}")
    print(f"Most likely born: {birth_years[0]} (Sept-Dec) or {birth_years[1]} (Jan-Aug)")
    print(f"Most likely current age: {birth_years[2]}-{birth_years[3]} years old")

def calculate_grade_from_birthday(month = 1, day = 1, year = 1990, as_of_year=None):
    """
    Calculate most likely grade level given a birthday.
    
    Assumes:
    - School year runs from September to June
    - Kindergarten starts at age 5-6
    - Students with birthdays Sept-Dec are typically younger in their grade
    - Students with birthdays Jan-Aug are typically older in their grade
    
    Args:
        month (int): Birth month (1-12)
        day (int): Birth day (1-31)
        year (int): Birth year
        as_of_year (int, optional): Calculate grade as of this year. Defaults to current year.
        
    Returns:
        str: Grade level description
    """
    if as_of_year is None:
        as_of_year = datetime.now().year
    
    # Calculate age as of September 1st of the school year
    birthday = datetime(year, month, day)
    sept_first = datetime(as_of_year, 9, 1)
    
    age_on_sept_first = (sept_first - birthday).days // 365
    
    # Kindergarten starts at age 5
    # Grade = age - 5
    grade = age_on_sept_first - 5
    
    if grade < 0:
        return f"Not yet in school (age {age_on_sept_first})"
    elif grade == 0:
        return "Kindergarten"
    elif grade <= 12:
        return f"Grade {grade}"
    else:
        years_since_hs = grade - 12
        return f"Graduated high school (~{years_since_hs} years ago)"   


# kx.pretty_print(calculate_grade_from_birthday(year = 1990))

from datetime import date

def estimate_age_from_grade_year(year_entering: int, grade_number: int, current_year: int = None):
    """
    Estimates current age based on entering a specific grade in a given year.
    Assumes typical US school system where students enter kindergarten at age 5.
    
    Args:
        year_entering: The year entering the specified grade
        grade_number: The grade number (K=0, 1st=1, 2nd=2, ..., 12th=12)
        current_year: The current year (defaults to today's year)
    
    Returns:
        Estimated current age
    """
    if current_year is None:
        current_year = date.today().year
    
    # Typical age when entering kindergarten
    kindergarten_entry_age = 5
    
    # Calculate typical age when entering the specified grade
    typical_age_at_grade = kindergarten_entry_age + grade_number
    
    # Calculate years passed since entering that grade
    years_passed = current_year - year_entering
    
    # Estimate current age
    estimated_age = typical_age_at_grade + years_passed
    
    return estimated_age


if __name__ == "__main__":
    # Example: entering 9th grade in summer 2015
    age = estimate_age_from_grade_year(year_entering=2015, grade_number=9)
    print(f"Estimated current age: {age} years old")
    
    # Other examples
    age_7th = estimate_age_from_grade_year(year_entering=2015, grade_number=7)
    print(f"If entering 7th grade in 2015: {age_7th} years old")
    
    age_college = estimate_age_from_grade_year(year_entering=2008, grade_number=13)
    print(f"If entering college (grade 13) in 2015: {age_college} years old")

