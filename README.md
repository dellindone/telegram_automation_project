# Telegram Automation Project

A Python-based Telegram subscription management automation system that uses **Google Sheets as the data store** and **Telethon for Telegram personal-account automation**.

The project manages Telegram group members based on their subscription status, sends subscription-expiry reminders, and removes users from the Telegram group when their subscription expires.

## Features

- Google Sheets integration
- Member management
- Subscription management
- Automatic subscription expiry-date calculation
- Configurable expiry reminders
- Telegram private messages through Telethon
- Removal of expired users from a Telegram group
- Marking successfully removed members as inactive
- Tracking removal failures
- Tracking reminder status
- Reminder cleanup after subscription removal
- Error tracking in Google Sheets

## Architecture

```text
                    ┌─────────────────────┐
                    │    Google Sheets    │
                    │                     │
                    │  members            │
                    │  subscriptions      │
                    │  reminders          │
                    │  reminder_config    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ GoogleSheetsClient  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Subscription       Reminder         Expiry Removal
        Processing        Processing         Processing
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   TelegramClient    │
                    │      Telethon       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Telegram Group/User │
                    └─────────────────────┘
```

Google Sheets is used as the persistent data store. Pandas DataFrames are used for in-memory processing.

## Project Structure

```text
telegram_automation_project/
├── credentials/
│   └── google-service-account.json
├── src/
│   ├── clients/
│   │   ├── google_sheets.py
│   │   └── telegram.py
│   ├── config/
│   │   ├── settings.py
│   │   └── sheets.py
│   ├── jobs/
│   │   └── expired_user_removal_job.py
│   ├── models/
│   │   ├── member.py
│   │   ├── remainder.py
│   │   └── subscription.py
│   ├── processes/
│   │   ├── create_remainders.py
│   │   ├── remove_expiry.py
│   │   ├── send_remainder.py
│   │   └── update_subscription.py
│   ├── services/
│   │   ├── expired_user_removal.py
│   │   ├── remainder.py
│   │   ├── remainder_sending.py
│   │   └── subscription.py
│   └── utils/
│       └── logger.py
├── .env
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Technology Stack

- Python
- Pandas
- Google Sheets
- gspread
- Google Service Account
- Pydantic
- Pydantic Settings
- python-dotenv
- Telethon

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dellindone/telegram_automation_project.git
cd telegram_automation_project
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Current dependencies:

```text
pandas
gspread
google-auth
pydantic
pydantic-settings
python-dotenv
telethon
```

## Environment Configuration

Create a `.env` file in the project root:

```env
GOOGLE_CREDENTIALS_FILE=credentials/google-service-account.json
GOOGLE_SHEET_ID=your_google_sheet_id

TELEGRAM_GROUP_ID=-100xxxxxxxxxx

TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+91xxxxxxxxxx
```

### Google Sheets Configuration

`GOOGLE_CREDENTIALS_FILE`

Path to the Google service-account JSON file.

Example:

```env
GOOGLE_CREDENTIALS_FILE=credentials/google-service-account.json
```

`GOOGLE_SHEET_ID`

The spreadsheet ID from the Google Sheets URL.

For:

```text
https://docs.google.com/spreadsheets/d/XXXXXXXXXXXXXXXX/edit
```

the spreadsheet ID is:

```text
XXXXXXXXXXXXXXXX
```

### Telegram Configuration

`TELEGRAM_GROUP_ID`

The Telegram group/supergroup ID where members are managed.

```env
TELEGRAM_GROUP_ID=-1001234567890
```

`TELEGRAM_API_ID`

Telegram API ID obtained from Telegram's developer platform.

`TELEGRAM_API_HASH`

Telegram API hash obtained along with the API ID.

`TELEGRAM_PHONE`

Phone number of the personal Telegram account used by Telethon.

## Google Sheets

The application uses four worksheets:

```text
members
subscriptions
reminders
reminder_config
```

## Members Sheet

The `members` worksheet stores Telegram member information.

| Column | Description |
|---|---|
| id | Internal member ID |
| telegram_user_id | Telegram numeric user ID |
| name | Member name |
| status | Member status |
| joined_date | Date the member joined |

Example:

```text
id | telegram_user_id | name   | status | joined_date
1  | 1090899134       | Aditya | active | 2026-09-01
```

The numeric `telegram_user_id` is used to identify the Telegram user.

When an expired user is successfully removed from Telegram:

```text
active → inactive
```

## Subscriptions Sheet

The `subscriptions` worksheet stores subscription history.

| Column | Description |
|---|---|
| id | Subscription ID |
| member_id | Reference to member ID |
| subscribe_date | Subscription start date |
| expired_after | Subscription duration in days |
| expiry_date | Calculated expiry date |
| status | Subscription status |
| removed_at | Date/time when user was removed |
| error | Error history |
| created_at | Record creation timestamp |
| updated_at | Last update timestamp |

Example:

```text
id | member_id | subscribe_date | expired_after | expiry_date | status
1  | 10        | 2026-09-01     | 30            | 2026-10-01  | active
```

## Subscription Lifecycle

A subscription starts as:

```text
active
```

When the expiry date is reached:

```text
active
   ↓
removal_pending
```

The system then attempts to remove the Telegram user.

If removal succeeds:

```text
removal_pending
        ↓
      removed
```

`removed_at` is populated and the corresponding member becomes inactive.

If removal fails:

```text
removal_pending
        ↓
removal_failed
```

The error is stored in the subscription record.

## Reminders Sheet

The `reminders` worksheet stores scheduled subscription reminders.

| Column | Description |
|---|---|
| id | Reminder ID |
| subscription_id | Related subscription |
| reminder_days | Number of days before expiry |
| scheduled_date | Date the reminder should be sent |
| sent_at | Date/time the reminder was sent |
| status | Reminder status |
| error | Error message |

Possible statuses:

```text
pending
sent
failed
```

## Reminder Configuration

The `reminder_config` worksheet controls which reminders are enabled.

| Column | Description |
|---|---|
| id | Configuration ID |
| reminder_days | Number of days before expiry |
| enabled | Whether the reminder is enabled |

Example:

```text
id | reminder_days | enabled
1  | 7             | TRUE
2  | 3             | TRUE
3  | 1             | TRUE
```

This configuration creates reminders 7, 3, and 1 day before expiry.

Reminder timing is therefore controlled from Google Sheets rather than `.env`.

## Application Flow

The main application performs:

```text
1. Update subscriptions
        ↓
2. Create reminders
        ↓
3. Send due reminders
        ↓
4. Remove expired users
```

## Step 1: Update Subscriptions

The subscription process reads the `subscriptions` sheet.

For every subscription it:

1. Reads `subscribe_date`
2. Reads `expired_after`
3. Calculates `expiry_date`
4. Initializes an empty status as `active`
5. Initializes `created_at` when required
6. Updates `updated_at` when a row changes

Example:

```text
subscribe_date = 2026-09-01
expired_after  = 30
expiry_date    = 2026-10-01
```

This process does not remove Telegram users.

## Step 2: Create Reminders

The reminder process reads:

```text
subscriptions
reminders
reminder_config
```

For each active subscription, it calculates:

```text
scheduled_date = expiry_date - reminder_days
```

Example:

```text
Expiry date = 2026-10-01

7-day reminder → 2026-09-24
3-day reminder → 2026-09-28
1-day reminder → 2026-09-30
```

Before creating a reminder, the system checks whether the same combination of:

```text
subscription_id + reminder_days
```

already exists. This prevents duplicate reminders.

## Step 3: Send Due Reminders

The reminder-sending process reads:

```text
reminders
subscriptions
members
```

It selects reminders where:

```text
status = pending
```

and:

```text
scheduled_date <= today
```

For each due reminder:

1. Find the related subscription.
2. Find the related member.
3. Get `telegram_user_id`.
4. Build the expiry message.
5. Send the message through Telethon.
6. Mark the reminder as `sent`.

Example message:

```text
Your Telegram group subscription will expire in 7 day(s) on 2026-10-01.
```

If sending fails, the reminder becomes:

```text
failed
```

and the error is stored.

## Step 4: Remove Expired Users

The expiry process reads:

```text
subscriptions
members
reminders
```

It selects active subscriptions whose:

```text
expiry_date <= today
```

Each expired subscription is processed individually.

### Removal Flow

```text
Expired subscription
        ↓
removal_pending
        ↓
Get telegram_user_id
        ↓
Remove user from Telegram
        ↓
      Success?
      /     \
    Yes      No
    ↓         ↓
removed   removal_failed
    ↓
member → inactive
    ↓
remove related reminders
```

The member is marked inactive only after the Telegram removal succeeds.

## Telegram Integration

The project uses **Telethon** for personal Telegram-account automation.

### Send Message

```python
await telegram.send_message(
    telegram_user_id=1090899134,
    message="Hello from Telethon!",
)
```

### Remove User

```python
await telegram.remove_user(
    telegram_user_id=1090899134,
)
```

The Telegram account must have sufficient permissions in the group to remove members.

## Telethon Session

Telethon creates:

```text
telegram_session.session
```

The session stores authentication state so the account does not need to authenticate on every run.

The session file must never be committed to Git and should be included in `.gitignore`.

### First Telegram Login

On the first run Telethon may request:

```text
Phone number
OTP
2FA password
```

After successful authentication, the session is saved locally.

## Running the Application

From the project root:

```bash
python main.py
```

The intended flow is:

```text
update_subscriptions()
        ↓
create_reminders()
        ↓
send_reminders()
        ↓
remove_expired_users()
```

## Data Relationships

The sheets are connected through IDs:

```text
members.id
    ↑
    │
subscriptions.member_id
```

and:

```text
subscriptions.id
    ↑
    │
reminders.subscription_id
```

Therefore:

```text
Member
  │
  └── Subscription
          │
          └── Reminder
```

Example:

```text
Member ID: 10

Subscription:
id = 25
member_id = 10

Reminder:
id = 100
subscription_id = 25
```

## Why Telegram User ID Is Used

The application uses the numeric:

```text
telegram_user_id
```

as the Telegram user identifier.

Telegram usernames are not used as the primary identifier because usernames are optional and can change.

## Google Sheets Client

`GoogleSheetsClient` handles communication with Google Sheets.

Main responsibilities include:

- Reading worksheets into Pandas DataFrames
- Updating changed cells
- Appending new rows
- Updating worksheet data

## Configuration Constants

Google Sheet names and column names are centralized in:

```text
src/config/sheets.py
```

Examples:

```python
SheetName.MEMBERS
SheetName.SUBSCRIPTIONS
SheetName.REMINDERS
SheetName.REMINDER_CONFIG
```

and:

```python
MemberColumn.TELEGRAM_USER_ID
SubscriptionColumn.EXPIRY_DATE
ReminderColumn.SCHEDULED_DATE
ReminderConfigColumn.REMINDER_DAYS
```

This keeps sheet names and column names centralized instead of hardcoding them throughout the services.

## Models

### Member

Represents a Telegram group member.

Statuses include:

```text
active
inactive
blocked
```

### Subscription

Represents a user's subscription.

The subscription model contains lifecycle states such as:

```text
active
removal_pending
removed
removal_failed
cancelled
```

### Reminder

Represents a scheduled subscription reminder.

Statuses:

```text
pending
sent
failed
```

## Error Handling

Errors are stored in Google Sheets.

Subscription errors are stored in:

```text
subscriptions.error
```

Reminder errors are stored in:

```text
reminders.error
```

Removal failures set:

```text
subscription.status = removal_failed
```

and store the error.

Example:

```text
2026-09-22 12:30:15 | ValueError: Member 10 not found.
```

## Security

Never commit these files or values:

```text
.env
credentials/
telegram_session.session
TELEGRAM_API_HASH
TELEGRAM_API_ID
Google service-account credentials
```

The `.env.example` file should contain placeholders only.

## Operational Requirements

### Google Sheets

The Google service account must have access to the target spreadsheet.

The spreadsheet must contain:

```text
members
subscriptions
reminders
reminder_config
```

The worksheet column names must match `src/config/sheets.py`.

### Telegram

The Telethon account must have the required permissions in the target group.

`TELEGRAM_GROUP_ID` must point to the intended group/supergroup.

## Design Philosophy

The project intentionally keeps the architecture simple.

It does not currently use:

- Database
- Redis
- Celery
- Repository layer
- Separate API server

Google Sheets is the persistence layer and Pandas is used for processing.

Responsibilities are separated into:

```text
Clients
    ↓
Services
    ↓
Processes
```

### Clients

External-system communication:

```text
GoogleSheetsClient
TelegramClient
```

### Services

Business logic:

```text
SubscriptionService
ReminderService
ReminderSendingService
ExpiredUserRemovalService
```

### Processes

Application workflows:

```text
update_subscription.py
create_remainders.py
send_remainder.py
remove_expiry.py
```

## End-to-End Example

Suppose:

```text
Member ID: 10
Telegram User ID: 1090899134
Subscription ID: 25
Subscribe Date: 2026-09-01
Expired After: 30 days
```

The system calculates:

```text
Expiry Date = 2026-10-01
```

With reminder configuration:

```text
7 days
3 days
1 day
```

the reminders become:

```text
2026-09-24 → 7-day reminder
2026-09-28 → 3-day reminder
2026-09-30 → 1-day reminder
```

On the expiry date:

```text
2026-10-01
```

the system:

```text
1. Marks the subscription as removal_pending
2. Gets the Telegram user ID
3. Removes the user from Telegram
4. Marks the subscription as removed
5. Stores removed_at
6. Marks the member as inactive
7. Removes associated reminder records
```

If Telegram removal fails:

```text
subscription.status = removal_failed
```

and the error is recorded.

## Current Limitations

The application currently uses Google Sheets as its persistence layer, so it is intended for a relatively small operational workload rather than a high-volume transactional system.

The Telegram integration uses a personal Telegram account through Telethon. The account must remain authenticated and have the required group permissions.

The current `update_changed_rows()` method requires the old and new DataFrames to have the same shape. Operations that delete rows from a worksheet, such as deleting completed reminders, require separate row-deletion handling.

## Future Improvements

Possible future improvements:

- Automatic import of existing Telegram group members
- Store Telegram usernames
- Telegram join-event processing
- Re-add users after subscription renewal
- Proper Google Sheet row deletion for processed reminders
- Scheduled execution
- More detailed logging
- Retry handling for failed Telegram operations
- Unit tests
- Better handling of Telegram permission and rate-limit errors

## License

Add the project's license information here if an open-source license is selected.
