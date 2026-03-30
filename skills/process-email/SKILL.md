---
name: process-email
description: Process email action items from /Needs_Action/. Use this skill whenever an EMAIL_ file exists in Needs_Action, or the user says "process email", "handle email", "reply to email". This skill categorizes emails (invoice, support, inquiry, urgent), drafts context-aware responses, and creates approval requests for unknown contacts or sensitive messages.
---

# process-email

Process an email action item from /Needs_Action/ - categorize, draft response, and handle approvals.

## Trigger

Use this skill when:
- An email file exists in `/Needs_Action/` (filename starts with EMAIL_)
- User says: "process email", "handle email", "reply to email"
- Gmail watcher creates a new email action file

## When NOT to Use

- DO NOT use for non-email items (use process-inbox instead)
- DO NOT use if email is already in /In_Progress/ or /Done/
- DO NOT use without reading the email file first

## Instructions

1. **Read the email file**
   - Read frontmatter: `type`, `from`, `subject`, `priority`
   - Read email content
   - Identify sender (known contact or new?)

2. **Categorize the email**
   - **Invoice Request**: Customer asking for invoice
   - **Support Request**: Customer needing help
   - **General Inquiry**: General questions
   - **Urgent**: Contains "urgent", "ASAP", "deadline"
   - **Spam/Low Priority**: Newsletters, marketing

3. **Determine response strategy**

   **Known Contact (in Company_Handbook.md contacts):**
   - Auto-draft response if low risk
   - Create approval if involves money or commitments

   **Unknown Contact:**
   - ALWAYS create approval request
   - Draft suggested response for review

4. **Draft the response**
   - Read Company_Handbook.md for tone and guidelines
   - Context-aware reply based on email content
   - Professional and helpful tone
   - Include relevant attachments if mentioned

5. **Create approval or send**
   - If known contact + low risk: Draft reply, create approval file
   - If unknown or high risk: Create approval with draft
   - Update status in original email file

6. **Move to appropriate folder**
   - /In_Progress/ if waiting for approval
   - /Done/ if processed and no action needed

## Email Categories & Responses

### Invoice Request
```
Subject: Re: Invoice Request
Body:
Hi [Name],

Thank you for your request. Please find attached Invoice #[number] for [period/service].

Amount: $[amount]
Due Date: [date]

Please let me know if you have any questions.

Best regards
```

### Support Request
```
Subject: Re: [Original Subject]
Body:
Hi [Name],

Thanks for reaching out. I understand you're [issue].

[Helpful response or next steps]

Let me know if you need anything else.

Best regards
```

### General Inquiry
```
Subject: Re: [Original Subject]
Body:
Hi [Name],

Thank you for your email. [Response to inquiry].

Please let me know if you have any other questions.

Best regards
```

## Output Format

```
## Email Processed

**From**: [sender]
**Subject**: [subject]
**Category**: [invoice|support|inquiry|urgent]

### Action Taken
- [Drafted response / Created approval / Moved to Done]

### Response Draft
[Draft content]

### Next Step
- [Awaiting approval / Sent / No action needed]
```

## Token Efficiency

- Reads one email file + Company_Handbook.md
- Drafts response without external API calls
- ~1500 tokens per email

## Related Skills

- `process-inbox`: General inbox processing
- `request-approval`: Creates approval files
- `gmail-watcher`: Detects new emails (Python script)
