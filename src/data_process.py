import json
import sqlite3
import logging
from typing import List, Dict
from config import JSON_DATA_FILE, DATABASE_FILE

class ProjectDatabase:
    """
    A class to manage the project database, including table creation, data insertion, and importing data from a JSON file.
    """

    def __init__(self, json_datafile: str = JSON_DATA_FILE, db_name: str = DATABASE_FILE):
        """
        Initialize the database connection and create required tables.
        
        :param json_datafile: Path to the JSON data file.
        :param db_name: Name of the SQLite database file.
        """
        self.json_name = json_datafile
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        """
        Create necessary tables in the database if they do not already exist.
        """
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT,
                    description_short TEXT,
                    description_full TEXT,
                    rewards_amount TEXT,
                    rewards_approximate_amount TEXT,
                    rewards_distribution_date TEXT,
                    links_website TEXT,
                    links_twitter TEXT,
                    links_telegram TEXT,
                    links_discord TEXT,
                    status TEXT,
                    last_updated TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    task TEXT,
                    difficulty TEXT,
                    deadline TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            logging.error("Error creating tables: %s", str(e))
            raise

    def insert_project(self, project: Dict):
        """
        Insert a single project into the database, including its associated requirements.
        
        :param project: A dictionary containing project details and associated requirements.
        """
        self.cursor.execute("""
            INSERT INTO projects (
                project_name, description_short, description_full,
                rewards_amount, rewards_approximate_amount, rewards_distribution_date,
                links_website, links_twitter, links_telegram, links_discord,
                status, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project["project_name"],
            project["description"]["short"],
            project["description"]["full"],
            project["rewards"]["amount"],
            project["rewards"]["approximate_amount"],
            project["rewards"]["distribution_date"],
            project["links"]["website"],
            project["links"]["social"]["twitter"],
            project["links"]["social"]["telegram"],
            project["links"]["social"]["discord"],
            project["status"],
            project["last_updated"]
        ))
        project_id = self.cursor.lastrowid

        for requirement in project.get("requirements", []):
            self.cursor.execute("""
                INSERT INTO requirements (project_id, task, difficulty, deadline)
                VALUES (?, ?, ?, ?)
            """, (project_id, requirement["task"], requirement["difficulty"], requirement["deadline"]))

        self.connection.commit()

    def load_projects_from_json(self):
        """
        Load projects from a JSON file and insert them into the database.
        """
        try:
            with open(self.json_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for project in data:
                self.insert_project(project)
        except FileNotFoundError as e:
            logging.error("JSON file not found: %s", str(e))
        except json.JSONDecodeError as e:
            logging.error("Error decoding JSON: %s", str(e))
        except Exception as e:
            logging.error("Unexpected error while loading projects: %s", str(e))

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()


class ProjectQueryInterface:
    """
    A class to interact with the project database and perform various queries.
    """

    def __init__(self, db_name: str = DATABASE_FILE):
        """
        Initialize the database connection for querying.
        
        :param db_name: Name of the SQLite database file.
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def _get_all_projects(self) -> list:
        """
        Retrieve the names of all projects in the database.
        
        :return: A list of project names.
        """
        try:
            self.cursor.execute("SELECT project_name FROM projects")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error("Error fetching all projects: %s", str(e))
            return []

    def _get_project_info(self, project_name: str) -> dict:
        """
        Retrieve detailed information about a specific project.
        
        :param project_name: The name of the project to retrieve.
        :return: A dictionary containing project details.
        """
        try:
            self.cursor.execute("SELECT * FROM projects WHERE project_name = ?", (project_name,))
            row = self.cursor.fetchone()
            if row:
                return {
                    "project_name": row[1],
                    "description_short": row[2],
                    "description_full": row[3],
                    "rewards_amount": row[4],
                    "rewards_approximate_amount": row[5],
                    "rewards_distribution_date": row[6],
                    "links_website": row[7],
                    "links_twitter": row[8],
                    "links_telegram": row[9],
                    "links_discord": row[10],
                    "status": row[11],
                    "last_updated": row[12]
                }
            return {}
        except sqlite3.Error as e:
            logging.error("Error fetching project info for '%s': %s", project_name, str(e))
            return {}

    def _get_requirements_by_project(self, project_name: str) -> list:
        """
        Retrieve the requirements associated with a specific project.
        
        :param project_name: The name of the project.
        :return: A list of dictionaries containing requirements.
        """
        try:
            self.cursor.execute("""
                SELECT r.task, r.difficulty, r.deadline
                FROM requirements r
                JOIN projects p ON r.project_id = p.id
                WHERE p.project_name = ?
            """, (project_name,))
            return [{"task": row[0], "difficulty": row[1], "deadline": row[2]} for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error("Error fetching requirements for project '%s': %s", project_name, str(e))
            return []

    def get_all_projects(self) -> list:
        """
        Retrieve a list of all project names.
        
        :return: A list of project names.
        """
        return self._get_all_projects()

    def get_project_info(self, project_name: str) -> dict:
        """
        Retrieve details of a specific project.
        
        :param project_name: The name of the project.
        :return: A dictionary containing project details.
        """
        return self._get_project_info(project_name)

    def get_requirements_by_project(self, project_name: str) -> list:
        """
        Retrieve a list of requirements for a specific project.
        
        :param project_name: The name of the project.
        :return: A list of dictionaries containing requirement details.
        """
        return self._get_requirements_by_project(project_name)

    def search_projects(self, key: str, value: str) -> List[Dict]:
        """
        Search for projects by a specific key and value.
        
        :param key: The database field to search in.
        :param value: The search term.
        :return: A list of dictionaries containing matching projects.
        """
        try:
            query = f"SELECT * FROM projects WHERE {key} LIKE ?"
            self.cursor.execute(query, (f"%{value}%",))
            rows = self.cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "project_name": row[1],
                    "description_short": row[2],
                    "description_full": row[3],
                    "rewards_amount": row[4],
                    "rewards_approximate_amount": row[5],
                    "rewards_distribution_date": row[6],
                    "links_website": row[7],
                    "links_twitter": row[8],
                    "links_telegram": row[9],
                    "links_discord": row[10],
                    "status": row[11],
                    "last_updated": row[12]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logging.error("Error searching projects with key '%s' and value '%s': %s", key, value, str(e))
            return []

    def filter_by_status(self, status: str) -> List[Dict]:
        """
        Filter projects based on their status.
        
        :param status: The status to filter by.
        :return: A list of projects with the specified status.
        """
        try:
            query = "SELECT * FROM projects WHERE status = ?"
            self.cursor.execute(query, (status,))
            rows = self.cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "project_name": row[1],
                    "description_short": row[2],
                    "description_full": row[3],
                    "rewards_amount": row[4],
                    "rewards_approximate_amount": row[5],
                    "rewards_distribution_date": row[6],
                    "links_website": row[7],
                    "links_twitter": row[8],
                    "links_telegram": row[9],
                    "links_discord": row[10],
                    "status": row[11],
                    "last_updated": row[12]
                }
                for row in rows
            ]
        except sqlite3.Error as e:
            logging.error("Error filtering projects by status '%s': %s", status, str(e))
            return []


    def group_by_status(self) -> Dict[str, List[Dict]]:
        """
        Group projects by their status and return as a dictionary.
        
        :return: A dictionary where keys are statuses and values are lists of projects with that status.
        """
        try:
            self.cursor.execute("SELECT status FROM projects GROUP BY status")
            statuses = [row[0] for row in self.cursor.fetchall()]

            grouped = {}
            for status in statuses:
                grouped[status] = self.filter_by_status(status)
            return grouped
        except Exception as e:
            logging.error("Error grouping projects by status '%s': %s", status, str(e))
            return {}

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
