"""motion_pool tags clips from their path only (no library needed for this test)."""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import motion_pool as M


class Tags(unittest.TestCase):
    def t(self, rel): return M.tags(rel)

    def test_roles_sex_mood(self):
        x = self.t("Motion_-_TalkListen/Listener_Agree_F.rlMotion")
        self.assertEqual((x["role"], x["sex"], x["mood"], x["sit"]), ("listen", "F", "calm", False))
        x = self.t("Motion_-_TalkListen/Talker_Agressively_M01.rlMotion")
        self.assertEqual((x["role"], x["sex"], x["mood"]), ("talk", "M", "angry"))
        x = self.t("โมชั่น/Motion/MixMoves Communication 200_Female/Sit/Legs Crossed_Response/Sad.iMotion")
        self.assertEqual((x["role"], x["sex"], x["mood"], x["sit"]), ("listen", "F", "sad", True))
        self.assertTrue(self.t("โมชั่น/Motion/MixMoves Communication 200_Male/Stand/Arms Crossed_Response/Angry.iMotion")["crossed"])

    def test_excluded(self):
        for rel in ("Studio Mocap - Conversation/x/Studio Mocap/Conversation/Chat/MovingChat_Met_F.rlMotion",   # walks
                    "@ giang - Mixamo Full Motion Pack for iClone/x/zombie_scratch_idle_mixamo.rlMotion",
                    "Two Handed Sword Animset/Idle/Idle01.iMotion",
                    "โมชั่น/Motion/MixMoves Communication 200_Male/Stand/Transitions/Stand03_to_StandTKI.iMotion",
                    "Sleep Anim Pack iC7.92/Sleep_Bed/Sleep01.iMotion"):
            self.assertIsNone(self.t(rel), rel)

    def test_sex_from_story(self):
        st = {"characters": {"อัมพร": {"voice": "หญิง"}, "อัมพร_คุย": {}, "ชัยยศ": {"role": "สามี"}}}
        self.assertEqual(M.sex_of("อัมพร_คุย", {}, st), "F")
        self.assertEqual(M.sex_of("ชัยยศ_ขาย", {}, st), "M")
        self.assertEqual(M.sex_of("ใครก็ได้", {}, st), "any")


if __name__ == "__main__":
    unittest.main()
