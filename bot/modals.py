# Form sent to caller of /practice. Built using Slack's Block Kit Builder.
PRACTICE_MODAL = {
    "type": "modal",
    "callback_id": "practice modal",
    "title": {
        "type": "plain_text",
        "text": "Announcer",
        "emoji": True
    },
    "submit": {
        "type": "plain_text",
        "text": "Submit",
        "emoji": True
    },
    "close": {
        "type": "plain_text",
        "text": "Cancel",
        "emoji": True
    },
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "emoji": True,
                "text": "Practice Announcement"
            }
        },
        {
            "type": "input",
            "block_id": "time_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "time",
            },
            "label": {
                "type": "plain_text",
                "text": "What time (e.g., 6-8 PM Tomorrow)?",
                "emoji": True
            }
        },
        {
            "type": "actions",
            "block_id": "actions_block",
            "elements": [
                {
                    "type": "datepicker",
                    "initial_date": "2020-08-22",
                    "action_id": "date_action",
                    "placeholder": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Select a date"
                    }
                },
                {
                    "type": "static_select",
                    "action_id": "location_action",
                    "placeholder": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Select a location"
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "SAC fields field 1",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "SAC fields field 2",
                                "emoji": True
                            },
                            "value": "value-1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "SAC fields field 3",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "SAC fields field 4",
                                "emoji": True
                            },
                            "value": "value-2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Burger Bowl",
                                "emoji": True
                            },
                            "value": "value-2"
                        }
                    ]
                }
            ]
        },
        {
            "type": "actions",
            "block_id": "roster_block",
            "elements": [
                {
                    "type": "checkboxes",
                    "action_id": "roster",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Tournamet & Reserve Roster Only",
                                "emoji": True
                            }
                        }
                    ]
                }
            ]
        },
        {
            "type": "input",
            "block_id": "comments_block",
            "element": {
                "type": "plain_text_input",
                "action_id": "comments",
            },
            "label": {
                "type": "plain_text",
                "text": "Special Comments (if none, \"N\")",
                "emoji": True
            }
        }
    ]
}
