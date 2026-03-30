# file-watcher

Monitor the /Inbox/ folder for newly dropped files and create action items.

## Trigger

Use this skill when:
- User says "check inbox", "any new files", "what's in the inbox"
- A file has been dropped into /Inbox/ (triggered by filesystem_watcher.py)
- During startup scan to catch any files dropped while offline

## Instructions

1. **Scan /Inbox/ for new files**
   - List all non-.gitkeep, non-.md files
   - Cross-check against `/Logs/processed_files.txt` to skip already-processed files

2. **For each new file found**

   a. **Categorize the file**

   | Extension | Category | Default Priority |
   |-----------|----------|-----------------|
   | .pdf | Document/PDF | medium |
   | .docx, .doc | Document/Word | medium |
   | .xlsx, .csv | Spreadsheet | medium |
   | .jpg, .png | Image | low |
   | .txt, .md | Text | medium |
   | .zip | Archive | low |
   | .json, .xml | Data | medium |

   b. **Check content for priority signals**
   - Filename contains: urgent, invoice, payment, legal, contract → HIGH
   - Filename contains: report, summary, review → MEDIUM
   - Everything else → MEDIUM

   c. **Create action file in /Needs_Action/**
   ```markdown
   ---
   type: file_drop
   original_name: <filename>
   category: <category>
   priority: <high|medium|low>
   dropped_at: <ISO timestamp>
   status: pending
   ---

   ## New File: <filename>

   A file has been dropped for processing.

   **Category**: <category>
   **Size**: <human-readable size>

   ## Suggested Actions
   - [ ] Inspect file content
   - [ ] Determine required action
   - [ ] Route to appropriate workflow
   - [ ] Move to /Done/ when complete
   ```

3. **Log the detection**
   - Use `audit-log` skill to record: `file_detected` action type

4. **Update Dashboard**
   - Increment Needs_Action count

## Notes

- The Python `filesystem_watcher.py` script does this automatically when running
- This skill is for manual/on-demand scanning
- Never process the same file twice (check processed_files.txt)
- If a file is too large to read (>10MB), just create the action file and note the size
