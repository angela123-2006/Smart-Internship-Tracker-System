-- ==============================================================
-- Smart Internship Tracker System — Database Schema
-- ==============================================================
-- Run this file to create the database, all tables, and sample data.
-- Usage:  mysql -u root -p < schema.sql
-- ==============================================================

CREATE DATABASE IF NOT EXISTS internship_tracker;
USE internship_tracker;

-- ==============================================================
-- 1. Students Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Students (
    Student_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Name          VARCHAR(100)  NOT NULL,
    Email         VARCHAR(150)  NOT NULL UNIQUE,
    Password_Hash VARCHAR(255)  NOT NULL,
    Department    VARCHAR(100)  NOT NULL,
    Resume_Path   VARCHAR(255)  DEFAULT NULL,
    CGPA          DECIMAL(3, 2) NOT NULL CHECK (CGPA >= 0 AND CGPA <= 10),
    Created_At    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==============================================================
-- 2. Companies Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Companies (
    Company_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Company_Name  VARCHAR(150)  NOT NULL,
    Email         VARCHAR(150)  NOT NULL UNIQUE,
    Password_Hash VARCHAR(255)  NOT NULL,
    Location      VARCHAR(150)  NOT NULL,
    Industry_Type VARCHAR(100)  NOT NULL,
    Website       VARCHAR(255),
    Created_At    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ==============================================================
-- 3. Internships Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Internships (
    Internship_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Company_ID           INT            NOT NULL,
    Role                 VARCHAR(150)   NOT NULL,
    Required_Skills      VARCHAR(500),
    Duration             VARCHAR(50)    NOT NULL,
    Stipend              DECIMAL(10, 2) DEFAULT 0.00,
    Application_Deadline DATE           NOT NULL,
    Created_At           TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (Company_ID) REFERENCES Companies(Company_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==============================================================
-- 4. Applications Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Applications (
    Application_ID     INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID         INT          NOT NULL,
    Internship_ID      INT          NOT NULL,
    Application_Date   DATE         NOT NULL,
    Application_Status ENUM('Applied', 'Interview Scheduled', 'Selected', 'Rejected')
                       DEFAULT 'Applied',
    Created_At         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (Student_ID)    REFERENCES Students(Student_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Internship_ID) REFERENCES Internships(Internship_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- Prevent duplicate applications
    UNIQUE KEY unique_application (Student_ID, Internship_ID)
) ENGINE=InnoDB;

-- ==============================================================
-- 5. Skills Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Skills (
    Skill_ID          INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID        INT          NOT NULL,
    Skill_Name        VARCHAR(100) NOT NULL,
    Proficiency_Level ENUM('Beginner', 'Intermediate', 'Advanced')
                      DEFAULT 'Beginner',

    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- A student should not have duplicate skill entries
    UNIQUE KEY unique_skill (Student_ID, Skill_Name)
) ENGINE=InnoDB;

-- ==============================================================
-- 6. Notifications Table
-- ==============================================================
CREATE TABLE IF NOT EXISTS Notifications (
    Notification_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Student_ID        INT          NOT NULL,
    Message           VARCHAR(500) NOT NULL,
    Notification_Date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ==============================================================
-- Indexes for performance on frequent queries
-- ==============================================================
CREATE INDEX idx_internship_deadline  ON Internships(Application_Deadline);
CREATE INDEX idx_application_status   ON Applications(Application_Status);
CREATE INDEX idx_notification_student ON Notifications(Student_ID);

-- ==============================================================
-- Sample Data
-- ==============================================================
-- Note: All sample passwords are "password123" hashed with bcrypt.
-- Hash: $2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim

-- Sample Students
INSERT INTO Students (Name, Email, Password_Hash, Department, CGPA) VALUES
    ('Aarav Sharma',  'aarav.sharma@college.edu',  '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Computer Science',       8.50),
    ('Priya Patel',   'priya.patel@college.edu',   '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Information Technology',  9.10),
    ('Rohan Gupta',   'rohan.gupta@college.edu',   '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Electronics',            7.80),
    ('Sneha Iyer',    'sneha.iyer@college.edu',    '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Computer Science',       8.90),
    ('Vikram Reddy',  'vikram.reddy@college.edu',  '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Mechanical Engineering', 7.20);

-- Sample Companies
INSERT INTO Companies (Company_Name, Email, Password_Hash, Location, Industry_Type, Website) VALUES
    ('TechNova Solutions',  'hr@technova.example.com',      '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Bangalore',  'Software',        'https://technova.example.com'),
    ('DataWave Analytics',  'hr@datawave.example.com',      '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Hyderabad',  'Data Science',    'https://datawave.example.com'),
    ('GreenByte Systems',   'hr@greenbyte.example.com',     '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Pune',       'Cloud Computing', 'https://greenbyte.example.com'),
    ('InnoVentures',        'hr@innoventures.example.com',  '$2b$12$LJ3m4ys4Ey5xQe6g5p1t1OuOQHVKRM1rGqHg6T0a7UEQEX7rK.Iim', 'Mumbai',     'FinTech',         'https://innoventures.example.com');

-- Sample Internships
INSERT INTO Internships (Company_ID, Role, Required_Skills, Duration, Stipend, Application_Deadline) VALUES
    (1, 'Backend Developer Intern',    'Python, Flask, SQL',           '3 months', 15000.00, '2026-04-30'),
    (1, 'Frontend Developer Intern',   'HTML, CSS, JavaScript, React', '3 months', 15000.00, '2026-04-30'),
    (2, 'Data Analyst Intern',         'Python, SQL, Pandas',          '6 months', 20000.00, '2026-05-15'),
    (3, 'Cloud Engineer Intern',       'AWS, Docker, Linux',           '4 months', 18000.00, '2026-04-20'),
    (4, 'FinTech Developer Intern',    'Python, REST APIs, SQL',       '3 months', 25000.00, '2026-05-01');

-- Sample Skills
INSERT INTO Skills (Student_ID, Skill_Name, Proficiency_Level) VALUES
    (1, 'Python',     'Advanced'),
    (1, 'Flask',      'Intermediate'),
    (1, 'SQL',        'Intermediate'),
    (2, 'Python',     'Advanced'),
    (2, 'Pandas',     'Advanced'),
    (2, 'SQL',        'Advanced'),
    (3, 'C++',        'Advanced'),
    (3, 'Arduino',    'Intermediate'),
    (4, 'JavaScript', 'Advanced'),
    (4, 'React',      'Advanced'),
    (4, 'Python',     'Intermediate'),
    (5, 'AutoCAD',    'Advanced'),
    (5, 'MATLAB',     'Intermediate');

-- Sample Applications
INSERT INTO Applications (Student_ID, Internship_ID, Application_Date, Application_Status) VALUES
    (1, 1, '2026-03-10', 'Applied'),
    (2, 3, '2026-03-11', 'Interview Scheduled'),
    (4, 2, '2026-03-12', 'Applied'),
    (1, 5, '2026-03-13', 'Selected');

-- Sample Notifications
INSERT INTO Notifications (Student_ID, Message) VALUES
    (1, 'Your application for Backend Developer Intern at TechNova Solutions has been received.'),
    (2, 'Interview scheduled for Data Analyst Intern at DataWave Analytics on 2026-03-25.'),
    (1, 'Congratulations! You have been selected for FinTech Developer Intern at InnoVentures.'),
    (4, 'Reminder: Application deadline for Frontend Developer Intern at TechNova is 2026-04-30.');
