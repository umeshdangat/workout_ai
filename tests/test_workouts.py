import unittest
from backend.api.workouts import parse_openai_response, WorkoutPlan
from backend.models.workouts import WOD, Strength, Session, Day, Week


class TestParseOpenAIResponse(unittest.TestCase):
    def setUp(self):
        # Raw JSON as a string (formatted correctly)
        self.raw_response = """{
            "name": "Ken G's Advanced CrossFit Program",
            "weeks": [
                {
                    "days": [
                        {
                            "sessions": [
                                {
                                    "type": "WOD",
                                    "details": {
                                        "description": "Grace",
                                        "intended_stimulus": "Fast-paced and high intensity",
                                        "scaling_options": "Reduce weight if needed, aim for quick transitions",
                                        "movements": [
                                            {
                                                "description": "Clean and Jerks (135/95 lbs)",
                                                "resources": "https://link.to/movement"
                                            }
                                        ]
                                    }
                                },
                                {
                                    "type": "Strength",
                                    "details": {
                                        "description": "Snatch Complex: Power Snatch + Overhead Squat",
                                        "sets": 5,
                                        "reps": "1+2",
                                        "intensity": "85% of 1RM Snatch",
                                        "rest": "2 minutes between sets",
                                        "notes": "Focus on speed and stability"
                                    }
                                }
                            ]
                        },
                        {
                            "sessions": [
                                {
                                    "type": "WOD",
                                    "details": {
                                        "description": "Murph",
                                        "intended_stimulus": "Endurance and mental toughness",
                                        "scaling_options": "Partition the reps if needed, focus on consistent pacing",
                                        "movements": [
                                            {
                                                "description": "1-mile Run, 100 Pull-ups, 200 Push-ups, 300 Air Squats, 1-mile Run",
                                                "resources": "https://link.to/movement"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }"""

    def test_parse_openai_response(self):
        # Parse the raw JSON into a WorkoutPlan object
        workout_plan = parse_openai_response(self.raw_response)

        # Assert the workout plan structure
        self.assertIsInstance(workout_plan, WorkoutPlan)
        self.assertEqual(workout_plan.name, "Ken G's Advanced CrossFit Program")
        self.assertEqual(len(workout_plan.weeks), 1)

        # Validate Week 1
        week_1 = workout_plan.weeks[0]
        self.assertIsInstance(week_1, Week)
        self.assertEqual(len(week_1.days), 2)

        # Validate Day 1
        day_1 = week_1.days[0]
        self.assertIsInstance(day_1, Day)
        self.assertEqual(len(day_1.sessions), 2)

        # Validate WOD Session in Day 1
        wod_session = day_1.sessions[0]
        self.assertIsInstance(wod_session, Session)
        self.assertEqual(wod_session.type, "WOD")
        self.assertIsInstance(wod_session.details, WOD)
        self.assertEqual(wod_session.details.description, "Grace")
        self.assertEqual(wod_session.details.intended_stimulus, "Fast-paced and high intensity")
        self.assertEqual(len(wod_session.details.movements), 1)
        self.assertEqual(wod_session.details.movements[0].description, "Clean and Jerks (135/95 lbs)")

        # Validate Strength Session in Day 1
        strength_session = day_1.sessions[1]
        self.assertIsInstance(strength_session, Session)
        self.assertEqual(strength_session.type, "Strength")
        self.assertIsInstance(strength_session.details, Strength)
        self.assertEqual(strength_session.details.description, "Snatch Complex: Power Snatch + Overhead Squat")
        self.assertEqual(strength_session.details.sets, "5")
        self.assertEqual(strength_session.details.reps, "1+2")

        # Validate Day 2
        day_2 = week_1.days[1]
        self.assertIsInstance(day_2, Day)
        self.assertEqual(len(day_2.sessions), 1)

        # Validate WOD Session in Day 2
        wod_day_2_session = day_2.sessions[0]
        self.assertIsInstance(wod_day_2_session, Session)
        self.assertEqual(wod_day_2_session.type, "WOD")
        self.assertIsInstance(wod_day_2_session.details, WOD)
        self.assertEqual(wod_day_2_session.details.description, "Murph")
        self.assertEqual(wod_day_2_session.details.intended_stimulus, "Endurance and mental toughness")
        self.assertEqual(len(wod_day_2_session.details.movements), 1)
        self.assertEqual(wod_day_2_session.details.movements[0].description, "1-mile Run, 100 Pull-ups, 200 Push-ups, 300 Air Squats, 1-mile Run")


if __name__ == "__main__":
    unittest.main()
