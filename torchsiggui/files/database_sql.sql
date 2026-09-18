-- DATABASE SETUP STATEMENTS

-- name: create_database()#
-- Creates the tables in the database file and adds initial values
CREATE TABLE IF NOT EXISTS worker_table (
  pid INTEGER NOT NULL PRIMARY KEY,
  created REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS file_table (
  id TEXT NOT NULL PRIMARY KEY,
  current_status TEXT NOT NULL,
  progress INTEGER NOT NULL,
  total INTEGER NOT NULL,
  filepath TEXT NOT NULL UNIQUE COLLATE NOCASE,
  complete INTEGER NOT NULL CHECK (complete IN (0, 1)),
  ready INTEGER NOT NULL CHECK (ready IN (0, 1)),
  cancelled INTEGER NOT NULL CHECK (cancelled IN (0, 1))
);
CREATE TABLE IF NOT EXISTS spectrogram_table (
  current_name TEXT NOT NULL PRIMARY KEY,
  complete INTEGER NOT NULL CHECK (complete IN (0, 1))
);
INSERT INTO spectrogram_table (current_name, complete)
  SELECT '', 1
  WHERE NOT EXISTS (
    SELECT 1 FROM spectrogram_table
);

-- name: clear_session_state()#
-- Removes the file and spectrogram records left by a previous session
DELETE FROM file_table;
UPDATE spectrogram_table SET current_name = '', complete = 1;



-- WORKER TABLE QUERY STATEMENTS

-- name: get_worker_count()$
-- Queries the total number of active workers
SELECT COUNT(*) from worker_table;

-- name: get_worker_info()
-- Queries the worker info stored in the worker table
SELECT pid, created FROM worker_table;



-- WORKER TABLE UPDATE STATEMENTS

-- name: add_worker_entry(process_id, created_date)!
-- Adds a worker entry to the worker table
INSERT INTO worker_table (pid, created)
  VALUES (:process_id, :created_date);

-- name: delete_worker_entry(process_id)!
-- Deletes a worker entry from the worker table
DELETE FROM worker_table WHERE pid = :process_id;



-- FILE TABLE QUERY STATEMENTS

-- name: get_file_info()
-- Queries the file info stored in the file table
SELECT id, current_status, progress, total, filepath, complete, ready FROM file_table;

-- name: get_is_cancelled(file_id)$
-- Queries whether the write for a file is cancelled
SELECT cancelled FROM file_table WHERE id = :file_id;

-- name: get_is_complete(file_id)$
-- Queries whether the write for a file is complete
SELECT complete FROM file_table WHERE id = :file_id;



-- FILE TABLE UPDATE STATEMENTS

-- name: add_file_entry(file_id, total, filepath)!
-- Adds a file entry to the file table
INSERT INTO file_table (id, current_status, progress, total, filepath, complete, ready, cancelled)
  VALUES (:file_id, '', 0, :total, :filepath, 0, 0, 0);

-- name: update_current_status(file_id, new_status)!
-- Updates the current status for a file entry
UPDATE file_table
  SET current_status = :new_status
  WHERE id = :file_id AND cancelled = 0;

-- name: update_file_progress(file_id)!
-- Updates the progress for a file entry and updates the current status accordingly
-- - Joins text with || rather than CONCAT, which older SQLite versions bundled with Python do not have
UPDATE file_table
  SET progress = progress + 1,
    current_status = CASE
      WHEN cancelled = 0 THEN '(' || (progress + 1) || '/' || total || ') Generating...'
      ELSE current_status
    END
  WHERE id = :file_id;

-- name: complete_file(file_id, complete_status)!
-- Marks a file entry as complete and, unless cancelled, ready to use
UPDATE file_table
  SET complete = 1,
    ready = CASE
      WHEN cancelled = 0 THEN 1
      ELSE 0
    END,
    current_status = CASE
      WHEN cancelled = 0 THEN :complete_status
      ELSE current_status
    END
  WHERE id = :file_id;

-- name: fail_file(file_id, error_status)!
-- Marks a file entry as complete without making it ready to use
UPDATE file_table
  SET complete = 1,
    current_status = CASE
      WHEN cancelled = 0 THEN :error_status
      ELSE current_status
    END
  WHERE id = :file_id;

-- name: cancel_file(file_id)!
-- Marks a file entry as cancelled
UPDATE file_table
  SET cancelled = 1,
    current_status = 'Cancelled'
  WHERE id = :file_id;

-- name: delete_file_entry(file_id)!
-- Deletes a file entry from the file table
DELETE FROM file_table WHERE id = :file_id;



-- SPECTROGRAM TABLE QUERY STATEMENTS

-- name: get_spectrogram_details()^
-- Queries the spectrogram details in the spectrogram table
SELECT current_name, complete FROM spectrogram_table;



-- SPECTROGRAM TABLE UPDATE STATEMENTS

-- name: update_start_spectrogram(new_name)!
-- Updates the next spectrogram filename in the spectrogram table
UPDATE spectrogram_table
  SET current_name = :new_name,
    complete = 0
  WHERE current_name != :new_name AND complete = 1;

-- name: update_complete_spectrogram()!
-- Marks the spectrogram as complete
UPDATE spectrogram_table SET complete = 1;