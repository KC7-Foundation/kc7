
# Constants related to email exfil
EMAIL_EXFIL_MAILBOX_FOLDER_NAMES = [
    "Inbox",
    "Drafts",
    "Sent Mail",
    "Deleted Mail",
    "Invoices",
    "Confidential",
    "Trade Deals"
]

EMAIL_EXFIL_OUTPUT_FILENAMES = [
    "contents",
    "email",
    "messages",
    "important"
]

EMAIL_EXFIL_OUTPUT_EXTENSIONS = [
    "7z",
    "zip",
    "rar",
    "gzip"
]

WEBSITE_STATIC_PATHS = [
    "home",
    "about",
    "contact",
    "covid19",
    "search?query=",
    "investor-relations",
    "about-us/history",
    "about-us/diversity",
    "faq",
    "about-us/leadership/executives",
    "careers",
    "careers/apply",
    "careers/company-culture",
    "careers/next-steps",
    "careers/internships",
    "careers/"
]

# common files on user comuters
COMMON_USER_FILE_LOCATIONS  = [
    "C:\\Users\\{username}\\Documents\\",
    "C:\\Users\\{username}\\Downloads\\",
    "C:\\Users\\{username}\\Pictures\\",
    "C:\\Users\\{username}\\Desktop\\",
    "C:\\Users\\{username}\\Videos\\",
    "C:\\Users\\{username}\Music\\"
]