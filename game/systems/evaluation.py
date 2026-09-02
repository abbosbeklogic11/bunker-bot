"""
game/systems/evaluation.py
Apocalyptic Survival Evaluation Engine for BUNKER game.
Performs an objective analysis comparing the bunker survivors' professions,
health, knowledge, and inventory against the specific apocalypse scenario.
Determines whether the team truly WON (survived) or LOST (perished).
"""
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ApocalypseEvaluator:
    @staticmethod
    def evaluate_survival(
        apocalypse: Dict[str, Any],
        survivors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates the team's chances of surviving the apocalypse in the bunker.
        Returns detailed score, player reviews, victory status, and narrative story.
        """
        if not survivors:
            return {
                "is_victory": False,
                "survival_chance": 0,
                "team_score": 0,
                "verdict_title": "💀 YUTQAZIQ! BUNKER BO'SH QOLDI!",
                "story": "Bunkerda hech kim qolmagani sababli insoniyat butunlay yo'q bo'ldi.",
                "player_reviews": [],
                "missing_skills": ["Barcha zarur mutaxassislar"]
            }

        prof_bonuses = apocalypse.get("profession_bonuses", {})
        health_penalties = apocalypse.get("health_penalties", {})
        know_bonuses = apocalypse.get("knowledge_bonuses", {})
        item_bonuses = apocalypse.get("item_bonuses", {})
        ap_type = apocalypse.get("type", "nuclear")
        ap_name = apocalypse.get("name", "Apokalipsis")
        duration_years = apocalypse.get("duration_years", 5)

        player_reviews = []
        total_team_raw_score = 0
        has_medical = False
        has_technical = False
        has_food_resource = False

        for p in survivors:
            name = p.get("name") or p.get("first_name", "O'yinchi")
            attrs = p.get("attributes", {})
            prof = attrs.get("profession", "")
            health = attrs.get("health", "")
            know = attrs.get("knowledge", "")
            inv = attrs.get("inventory", "")
            char = attrs.get("character", "")
            gen = attrs.get("genetics", "")

            score = 15  # base score per healthy human
            reasons = []

            # 1. Profession Matching
            matched_prof = False
            for k, bonus in prof_bonuses.items():
                if k.lower() in prof.lower() or prof.lower() in k.lower():
                    score += bonus
                    reasons.append(f"👨‍💼 {k} (+{bonus})")
                    matched_prof = True
                    break

            if "shifokor" in prof.lower() or "jarroh" in prof.lower() or "feldsher" in prof.lower():
                has_medical = True
            if "muhandis" in prof.lower() or "santexnik" in prof.lower() or "energetik" in prof.lower() or "mexanik" in prof.lower():
                has_technical = True
            if "fermer" in prof.lower() or "biolog" in prof.lower() or "oshpaz" in prof.lower():
                has_food_resource = True

            # If useless/passive profession for disaster
            useless_keywords = ["musiqachi", "rassom", "blogger", "aktyor", "kosmetolog", "model", "striptizchi", "tamadasi"]
            if any(u in prof.lower() for u in useless_keywords):
                score -= 10
                reasons.append(f"⚠️ {prof} (falokatda yordam bermaydi -10)")

            # 2. Health Check
            for k, penalty in health_penalties.items():
                if k.lower() in health.lower():
                    score += penalty  # penalty is negative
                    reasons.append(f"💔 {k} ({penalty})")

            bad_health_keywords = ["saraton", "rak", "og'ir", "falaj", "oits", "surunkali", "ko'r", "zaif"]
            if any(b in health.lower() for b in bad_health_keywords):
                score -= 15
                reasons.append("⚠️ Og'ir sog'liq muammosi (-15)")
            elif "sog'lom" in health.lower() or "a'lo" in health.lower():
                score += 10
                reasons.append("❤️ Mustahkam sog'liq (+10)")

            # 3. Knowledge Matching
            for k, bonus in know_bonuses.items():
                if k.lower() in know.lower() or know.lower() in k.lower():
                    score += bonus
                    reasons.append(f"🎓 {k} (+{bonus})")
                    break

            # 4. Inventory Matching
            for k, bonus in item_bonuses.items():
                if k.lower() in inv.lower() or inv.lower() in k.lower():
                    score += bonus
                    reasons.append(f"🎒 {k} (+{bonus})")
                    break

            crucial_items = ["filtr", "generator", "dozimetr", "dori", "qurol", "konserva", "urug'", "antiseptik"]
            for ci in crucial_items:
                if ci in inv.lower():
                    score += 10
                    reasons.append(f"🎒 Muhim buyum: {inv[:20]} (+10)")
                    break

            # 5. Character & Genetics
            if "yetakchi" in char.lower() or "mehnatkash" in char.lower() or "irodali" in char.lower():
                score += 8
                reasons.append("🧠 Ijobiy xarakter (+8)")
            elif "psixopat" in char.lower() or "vahimachi" in char.lower() or "tajovuzkor" in char.lower():
                score -= 15
                reasons.append("🧠 Xavfli xarakter (-15)")

            if "immunitet" in gen.lower() or "chidamli" in gen.lower():
                score += 10
                reasons.append("🧬 Kuchli genetika (+10)")
            elif "irsiy" in gen.lower() or "bepusht" in gen.lower() or "mutatsiya" in gen.lower():
                score -= 10
                reasons.append("🧬 Zaif genetika (-10)")

            # Role tag
            if score >= 35:
                tag = "🌟 Muhim mutaxassis (Hal qiluvchi)"
            elif score >= 15:
                tag = "✅ Foydali a'zo"
            elif score >= 0:
                tag = "⚠️ Neytral (Yordamchi)"
            else:
                tag = "❌ Jamoaga og'irlik"

            total_team_raw_score += score
            player_reviews.append({
                "name": name,
                "profession": prof,
                "score": score,
                "tag": tag,
                "reasons": reasons
            })

        # Calculate final survival probability (0% - 100%)
        # For a balanced team, 50 points per player on average is ideal (e.g. 100 pts for 2 players)
        expected_points = len(survivors) * 35
        survival_chance = int(min(100, max(5, (total_team_raw_score / max(1, expected_points)) * 65)))

        # Specific disaster critical checks
        missing_skills = []
        if not has_medical and ap_type in ("virus", "nuclear", "zombie", "pandemic"):
            survival_chance -= 20
            missing_skills.append("Tibbiy mutaxassis (Shifokor/Jarroh)")

        if not has_technical and ap_type in ("flood", "ice_age", "ai_rebellion", "meteor"):
            survival_chance -= 20
            missing_skills.append("Texnik mutaxassis (Muhandis/Santexnik/Mexanik)")

        survival_chance = min(99, max(5, survival_chance))
        is_victory = survival_chance >= 50

        # Generate narrative verdict
        if is_victory:
            verdict_title = "🎉 G'ALABA! BUNKER FALOKATNI YENGIB O'TDI!"
            story = (
                f"Jamoaning kasbiy mahorati, mustahkam sog'lig'i va to'g'ri tanlangan inventarlari tufayli "
                f"bunker <b>{duration_years} yil</b> davomida to'liq avtonom tarzda faoliyat yuritdi.\n\n"
                f"Qolgan o'yinchilar falokat davrini muvaffaqiyatli o'tkazib, bunker eshiklarini ochdilar "
                f"va yer yuzida <b>yangi insoniyat sivilizatsiyasiga</b> asos soldilar! 🌅"
            )
        else:
            verdict_title = "💀 YUTQAZIQ! BUNKER HALOKATGA UCHRADI!"
            missing_str = ", ".join(missing_skills) if missing_skills else "Zarur mutaxassislar va vositalar"
            story = (
                f"Afsuski, bunkerga kirgan jamoada <b>{ap_name}</b> uchun zarur ko'nikmalar "
                f"({missing_str}) yetishmadi yoki foydasiz kasblar/og'ir kasalliklar ko'p bo'ldi.\n\n"
                f"Oqibatda, bunker tizimlari buzilib, oziq-ovqat va tibbiy resurslar tugagach, "
                f"jamoa <b>{max(1, duration_years // 2)} yil</b> o'tib halokatga uchradi... 🪦"
            )

        return {
            "is_victory": is_victory,
            "survival_chance": survival_chance,
            "team_score": total_team_raw_score,
            "verdict_title": verdict_title,
            "story": story,
            "player_reviews": player_reviews,
            "missing_skills": missing_skills
        }
