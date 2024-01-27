import sqlite3
from dotenv import load_dotenv, find_dotenv, set_key
import os
import logging

logging.basicConfig(level=logging.DEBUG)


def get_env(thing: str) -> str:
    load_dotenv(find_dotenv())
    return os.getenv(thing)


def set_env(thing: str, new: str) -> None:
    os.environ[thing] = new
    set_key(find_dotenv(), thing, os.environ[thing])


def create_db() -> None:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS Surveys (
        sid        INTEGER    NOT NULL,                 
        name      TEXT    NOT NULL,
        author    INTEGER NOT NULL,        
        date      TEXT    NOT NULL,        
        questions TEXT    NOT NULL);''')
    conn.commit()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS Answers (
        survey  INTEGER REFERENCES Surveys (sid)                     NOT NULL,    
        user    INTEGER NOT NULL,       
        answers TEXT    NOT NULL);''')
    conn.commit()
    conn.close()


def create_survey(name: str, user: int, date: str, questions: List[str]) -> int:
    DB_NAME = get_env("DB_NAME")
    LID = int(get_env("LID")) + 1
    conn = sqlite3.connect(DB_NAME)
    print(DB_NAME, LID)
    cur = conn.cursor()
    cur.execute(
        f'''INSERT INTO Surveys (sid, name, author, date, questions)
        VALUES(\'{LID}\', \'{name}\', \'{user}\', \'{date}\', \'{'|'.join([question.replace('|', '') for question in questions])}\');''')
    conn.commit()
    conn.close()
    set_env("LID", str(LID))
    return LID


def create_answer(survey: int, user: int, answers: List[str]) -> None:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        f'''INSERT INTO Answers (survey, user, answers)
        VALUES(\'{survey}\', \'{user}\', \'{'|'.join([answer.replace('|', '') for answer in answers])}\');''')
    conn.commit()
    conn.close()


def get_survey(sid: int) -> List[int, str, int, str, str]:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    survey = cur.execute(
        f'''SELECT * FROM Surveys
        WHERE sid = {sid}''')
    survey = list(*survey)
    conn.close()
    return survey


def get_surveys(rowid_range: (int, int)) -> List[int, str]:  # type: ignore
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    st = ', '.join([f'\"{border}\"' for border in range(
        rowid_range[0], rowid_range[1] + 1)])
    surveys = cur.execute(
        f'''SELECT sid, name FROM Surveys
        WHERE rowid in ({st})''')
    surveys = list(surveys)
    conn.close()
    return surveys


def get_answers_by_sid(sid: int) -> List[tuple[int, str]]:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    answers = cur.execute(
        f'''SELECT user, answers FROM Answers
        WHERE survey = {sid}''')
    answers = list(answers)
    conn.close()
    return answers


def get_answer_by_uid(uid: int) -> List[int, str]:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    answers = cur.execute(
        f'''SELECT rowid FROM Answers
        WHERE user = {uid}''')
    answers = [answer[0] for answer in answers]
    conn.close()
    return answers


def get_surveys_by_answers_by_uid(uid: int) -> List[List[int, int]]:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    answers = cur.execute(
        f'''SELECT survey FROM Answers
        WHERE user = {uid}''')
    surveys = []
    answers = list(answers)
    for answer in answers:
        survey = cur.execute(
            f'''SELECT sid, name FROM Surveys
            WHERE sid = {answer[0]}''')
        surveys.append(list(survey))
    conn.close()
    return surveys


def get_surveys_by_uid(uid: int) -> List[List[int, int]]:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    surveys = cur.execute(
        f'''SELECT sid, name FROM Surveys
        WHERE author = {uid}''')
    surveys = list(surveys)
    print(surveys)
    conn.close()
    return surveys


def delete_survey(sid: int) -> None:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        f'''DELETE FROM Surveys
        WHERE sid = {sid}''')
    cur.execute('''REINDEX Surveys''')
    cur.execute(
        f'''DELETE FROM Answers
            WHERE survey = {sid}''')
    conn.commit()
    cur.execute('''VACUUM;''')
    conn.close()


def change_survey(sid: int, name: str, questions: List[str]) -> None:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        f'''UPDATE Surveys
            SET name = \'{name}\',
            questions = \'{'|'.join([question.replace('|', '') for question in questions])}\'
            WHERE sid = {sid}''')
    conn.commit()
    conn.close()


def delete_all_data() -> None:
    DB_NAME = get_env("DB_NAME")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        f'''DELETE FROM Surveys;''')
    cur.execute(
        f'''DELETE FROM Answers;''')
    conn.commit()
    conn.close()
    set_env("LID", str(0))
