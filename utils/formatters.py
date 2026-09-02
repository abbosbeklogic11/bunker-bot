"""
Message formatters for BUNKER game.
Provides rich, beautiful Uzbek UI formatting for group dashboards, cards, abilities, profiles, and final results.
"""
from typing import Dict, Any, List, Optional, Tuple


def get_player_status_emoji(status: str) -> str:
    """Returns status emoji."""
    st = status.upper() if status else "ACTIVE"
    if st in ("ACTIVE", "ALIVE"):
        return "🟢"
    elif st == "PROTECTED":
        return "🛡️"
    elif st == "ELIMINATED":
        return "🔴"
    elif st == "LEFT":
        return "🚪"
    elif st == "WINNER":
        return "🏆"
    elif st == "LOSER":
        return "❌"
    return "⚪"


def format_timer_text(seconds: int) -> str:
    """Formats seconds as MM:SS."""
    if seconds < 0:
        seconds = 0
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


def format_lobby_message(game_id: int, players: List[Dict[str, Any]], max_players: int = 20, min_players: int = 5) -> str:
    """Formats the interactive lobby announcement in the group chat."""
    count = len(players)
    sep = "━" * 22
    
    player_lines = []
    for idx, p in enumerate(players, 1):
        name = p.get("name") or p.get("first_name", "O'yinchi")
        player_lines.append(f"{idx}. 🟢 {name}")

    players_text = "\n".join(player_lines) if player_lines else "<i>Hozircha hech kim qo'shilmadi</i>"

    status_note = "🟢 <b>LOBBY TO'LDI! Boshlanmoqda...</b>" if count >= max_players else "⏳ <i>Boshlanishini kutmoqda...</i>"

    return (
        f"🏢 <b>BUNKER — YANGI O'YIN</b>\n"
        f"{sep}\n"
        f"👥 <b>O'yinchilar:</b> {count}/{max_players}\n"
        f"🎯 <b>Minimal talab:</b> {min_players} kishi\n"
        f"🏆 <b>G'oliblar soni:</b> 4 kishi\n"
        f"{status_note}\n\n"
        f"📋 <b>Qo'shilganlar:</b>\n{players_text}\n"
        f"{sep}\n"
        f"💡 <i>Qo'shilish uchun botni <b>/start</b> qilgan bo'lishingiz shart!</i>"
    )


def format_dashboard(
    round_num: int,
    phase: str,
    time_left: int,
    apocalypse: Dict[str, Any],
    bunker: Dict[str, Any],
    alive_count: int,
    total_count: int,
    capacity: int,
    revealed_types: List[str]
) -> str:
    """Formats the live pinned game dashboard."""
    sep = "━" * 22
    time_str = format_timer_text(time_left)

    phase_uzbek = {
        "STARTING": "🚀 O'YIN BOSHLANMOQDA",
        "DEAL_CARDS": "🃏 KARTALAR TARQATILMOQDA",
        "REVEAL_ATTRIBUTE": "🔓 XUSUSIYATLAR OCHILMOQDA",
        "DISCUSSION": "⏱ MUHOKAMA",
        "ABILITY_PHASE": "⚡ QOBILIYATLAR ISHLATISH",
        "VOTING": "🗳 OVOZ BERISH",
        "DUEL": "⚔️ DUEL (TENG KELGANLAR)",
        "ELIMINATION": "🚨 CHIQARISH BOSQICHI",
        "EVENT": "⚠️ FAVQULODDA HODISA",
        "FINAL": "🏆 FINAL BOSQICHI",
        "FINISHED": "🏁 O'YIN YAKUNLANDI"
    }.get(phase, phase)

    attr_labels = {
        "profession": "👨‍💼 Kasb",
        "age": "🎂 Yosh",
        "health": "❤️ Sog'liq",
        "character": "🧠 Xarakter",
        "hobby": "🎯 Hobbi",
        "knowledge": "🎓 Bilim",
        "genetics": "🧬 Genetika",
        "physical": "🏋️ Jismoniy holat",
        "inventory": "🎒 Inventar / Bagaj",
        "special": "🔬 Maxsus xususiyat"
    }

    revealed_str = "\n".join([f"  ✅ {attr_labels.get(t, t)}" for t in revealed_types]) or "  <i>Hali ochilmadi</i>"

    all_types = list(attr_labels.keys())
    hidden_types = [t for t in all_types if t not in revealed_types]
    hidden_str = "\n".join([f"  🔒 {attr_labels.get(t, t)}" for t in hidden_types]) or "  <i>Barchasi ochiq</i>"

    return (
        f"🏢 <b>BUNKER — RAUND #{round_num}</b>\n"
        f"{sep}\n"
        f"{apocalypse.get('emoji', '☢️')} <b>Apokalipsis:</b> {apocalypse.get('name', 'Nomaʼlum')}\n"
        f"👥 <b>Tirik qolganlar:</b> {alive_count}/{total_count}\n"
        f"🏠 <b>Bunker sig'imi:</b> {capacity} ta joy qoldi\n\n"
        f"⏱ <b>Bosqich:</b> <b>{phase_uzbek}</b>\n"
        f"⏳ <b>Qolgan vaqt:</b> <code>{time_str}</code>\n"
        f"{sep}\n"
        f"🔓 <b>Ochilgan xususiyatlar:</b>\n{revealed_str}\n\n"
        f"🔒 <b>Yopiq xususiyatlar:</b>\n{hidden_str}\n"
        f"{sep}"
    )


def format_player_list(players: List[Dict[str, Any]]) -> str:
    """Formats the player status list popup."""
    lines = ["👥 <b>O'YINCHILAR RO'YXATI:</b>\n"]
    for idx, p in enumerate(players, 1):
        st_emoji = get_player_status_emoji(p.get("status", "ACTIVE"))
        name = p.get("name") or p.get("first_name", "O'yinchi")
        prot = " 🛡️ [HIMOYALANGAN]" if p.get("is_protected") else ""
        elim = " — <i>chiqarildi</i>" if p.get("status") == "ELIMINATED" else ""
        lines.append(f"{idx}. {st_emoji} <b>{name}</b>{prot}{elim}")
    return "\n".join(lines)


def format_attributes_by_type(attr_type: str, revealed_data: List[Tuple[int, str, bool, str, str]]) -> str:
    """Formats group view for a specific revealed attribute."""
    titles = {
        "profession": "👨‍💼 O'YINCHILAR KASBLARI",
        "age": "🎂 O'YINCHILAR YOSHI",
        "health": "❤️ O'YINCHILAR SOG'LIG'I",
        "character": "🧠 O'YINCHILAR XARAKTERI",
        "hobby": "🎯 O'YINCHILAR HOBBILARI",
        "knowledge": "🎓 O'YINCHILAR BILIMLARI",
        "genetics": "🧬 O'YINCHILAR GENETIKASI",
        "physical": "🏋️ JISMONIY HOLATLAR",
        "inventory": "🎒 O'YINCHILAR INVENTARI",
        "special": "🔬 MAXSUS XUSUSIYATLAR"
    }
    title = titles.get(attr_type, f"📋 {attr_type.upper()}")
    sep = "━" * 22

    lines = [f"<b>{title}</b>", sep]
    for idx, (uid, val, is_fake, first_name, username) in enumerate(revealed_data, 1):
        lines.append(f"{idx}. <b>{first_name}:</b> {val}")
    lines.append(sep)
    return "\n".join(lines)


def format_private_cards(game_id: int, data: Dict[str, Any]) -> str:
    """Formats secret private cards message sent exclusively to player's private chat."""
    attrs = data.get("attributes", {})
    sep = "━" * 22

    return (
        f"🤫 <b>SIZNING MAXFIY MA'LUMOTLARINGIZ</b> (O'yin #{game_id})\n"
        f"<i>Bu ma'lumotlarni hech kimga ko'rsatmang!</i>\n"
        f"{sep}\n"
        f"👨‍💼 <b>Kasb:</b> {attrs.get('profession', 'Nomaʼlum')}\n"
        f"🎂 <b>Yosh:</b> {attrs.get('age', 'Nomaʼlum')}\n"
        f"❤️ <b>Sog'liq:</b> {attrs.get('health', 'Nomaʼlum')}\n"
        f"🧠 <b>Xarakter:</b> {attrs.get('character', 'Nomaʼlum')}\n"
        f"🎯 <b>Hobbi:</b> {attrs.get('hobby', 'Nomaʼlum')}\n"
        f"🎓 <b>Bilim:</b> {attrs.get('knowledge', 'Nomaʼlum')}\n"
        f"🧬 <b>Genetika:</b> {attrs.get('genetics', 'Nomaʼlum')}\n"
        f"🏋️ <b>Jismoniy:</b> {attrs.get('physical', 'Nomaʼlum')}\n"
        f"🎒 <b>Inventar:</b> {attrs.get('inventory', 'Nomaʼlum')}\n"
        f"🔬 <b>Maxsus:</b> {attrs.get('special', 'Nomaʼlum')}\n"
        f"{sep}\n"
        f"⚡ <i>Qobiliyatlaringiz va maxfiy kartalaringizni pastdagi tugmalar orqali boshqaring!</i>"
    )


def format_vote_results(vote_counts: Dict[int, int], players: Dict[int, str]) -> str:
    """Formats voting tally announcement."""
    lines = ["🗳 <b>OVOZ BERISH NATIJALARI:</b>\n"]
    for uid, count in sorted(vote_counts.items(), key=lambda x: x[1], reverse=True):
        name = players.get(uid, f"O'yinchi #{uid}")
        lines.append(f"👤 <b>{name}</b> — <b>{count} ta ovoz</b>")
    return "\n".join(lines)


def format_elimination_message(player_name: str, vote_count: int, remaining: int) -> str:
    """Formats player elimination notice."""
    sep = "━" * 22
    return (
        f"🚨 <b>O'YINCHI BUNKERDAN CHIQARILDI!</b>\n"
        f"{sep}\n"
        f"👤 <b>Chiqarilgan:</b> <s>{player_name}</s>\n"
        f"🗳 <b>Olingan ovozlar:</b> {vote_count} ta\n"
        f"👥 <b>Bunkerda qolganlar:</b> {remaining} kishi\n"
        f"{sep}\n"
        f"💀 <i>Tashqaridagi xavfli muhitda omon qolish imkonsiz...</i>"
    )


def format_duel_message(candidates: List[str], time_sec: int) -> str:
    """Formats tie-breaker duel announcement."""
    sep = "━" * 22
    cand_str = " VS ".join([f"<b>{c}</b>" for c in candidates])
    return (
        f"⚠️ <b>DURANG HOLATI ANIQLANDI!</b>\n"
        f"{sep}\n"
        f"⚔️ <b>DUEL:</b> {cand_str}\n\n"
        f"⏱ <b>Vaqt:</b> {format_timer_text(time_sec)}\n"
        f"🗣 <i>Nomzodlar o'zlarini himoya qilish uchun oxirgi dalillarini keltiradilar!</i>\n"
        f"🗳 <i>Keyin faqat shu nomzodlar orasida qayta ovoz beriladi!</i>\n"
        f"{sep}"
    )


def format_event_message(event: Dict[str, Any], resolved: bool, resolvers: List[Dict[str, Any]], consequences: Dict[str, Any]) -> str:
    """Formats random crisis event group notice."""
    sep = "━" * 22
    name = event.get("name", "Favqulodda Hodisa")
    emoji = event.get("emoji", "⚠️")
    desc = event.get("description", "")

    if resolved:
        res_names = ", ".join([f"<b>{r['name']}</b> ({r['reason']})" for r in resolvers])
        res_text = f"✅ <b>HODISA BARTARAF ETILDI!</b>\n👥 <b>Qutqarganlar:</b> {res_names}\n<i>{event.get('if_resolved_description', '')}</i>"
    else:
        res_text = f"❌ <b>HODISA BARTARAF ETILMADI!</b>\n<i>{event.get('if_not_resolved_description', '')}</i>"

    return (
        f"{emoji} <b>BUNKERDA HODISA: {name}</b>\n"
        f"{sep}\n"
        f"📋 {desc}\n\n"
        f"{res_text}\n"
        f"{sep}"
    )


def format_game_over(
    winners: List[Dict[str, Any]],
    apocalypse: Dict[str, Any],
    total_started: int,
    evaluation: Optional[Dict[str, Any]] = None
) -> str:
    """Formats the grand finale winning announcement with apocalypse evaluation."""
    sep = "━" * 22
    medals = ["🥇", "🥈", "🥉", "🏅"]

    winner_lines = []
    if evaluation and "player_reviews" in evaluation:
        for idx, pr in enumerate(evaluation["player_reviews"]):
            medal = medals[idx] if idx < len(medals) else "⭐"
            winner_lines.append(
                f"{medal} <b>{pr['name']}</b> ({pr.get('profession', '')})\n"
                f"   └ <i>{pr['tag']} ({pr['score']} ball)</i>"
            )
    else:
        for idx, w in enumerate(winners):
            medal = medals[idx] if idx < len(medals) else "⭐"
            name = w.get("name") or w.get("first_name", "O'yinchi")
            winner_lines.append(f"{medal} <b>{name}</b>")

    winners_text = "\n".join(winner_lines)

    verdict_title = evaluation.get("verdict_title", "🏆 BUNKER YAKUNI!") if evaluation else "🏆 BUNKER O'YINI YAKUNLANDI!"
    chance = evaluation.get("survival_chance", 75) if evaluation else 75
    story = evaluation.get("story", "") if evaluation else ""

    chance_emoji = "🟢" if chance >= 70 else ("🟡" if chance >= 50 else "🔴")

    res = [
        f"🏆 <b>BUNKER O'YINI YAKUNLANDI!</b>",
        sep,
        f"<b>{verdict_title}</b>",
        f"{chance_emoji} <b>Omon qolish ehtimoli:</b> {chance}%\n",
        f"📜 <b>Tarixiy xulosa:</b>\n<i>{story}</i>\n",
        sep,
        f"👥 <b>BUNKERGA KIRGAN G'OLIBLAR:</b>\n{winners_text}\n",
        sep,
        f"🌍 <b>Falokat:</b> {apocalypse.get('emoji', '☢️')} {apocalypse.get('name', 'Apokalipsis')}",
        f"👥 <b>Boshlaganlar:</b> {total_started} ta",
        f"🏆 <b>Bunkerga kirganlar:</b> {len(winners)} ta",
        f"💀 <b>Chiqarilganlar:</b> {max(0, total_started - len(winners))} ta",
        sep,
        f"🎁 <i>G'oliblarga Coins, Diamonds va tajriba ballari yuborildi!</i>"
    ]
    return "\n".join(res)


def format_profile(user: Dict[str, Any], achievements: List[Dict[str, Any]]) -> str:
    """Formats player profile display."""
    sep = "━" * 22
    name = user.get("first_name", "Foydalanuvchi")
    username = f" (@{user.get('username')})" if user.get("username") else ""
    
    played = user.get("games_played", 0)
    won = user.get("games_won", 0)
    lost = user.get("games_lost", 0)
    win_rate = round((won / played * 100), 1) if played > 0 else 0.0

    ach_text = ", ".join([f"{a.get('icon', '⭐')} {a.get('name')}" for a in achievements[:5]]) if achievements else "<i>Hali yutuqlar yo'q</i>"

    return (
        f"👤 <b>OYINCHI PROFILI: {name}</b>{username}\n"
        f"{sep}\n"
        f"⭐ <b>Level:</b> {user.get('level', 1)}\n"
        f"🪙 <b>Coins:</b> {user.get('coins', 0):,}\n"
        f"💎 <b>Diamonds:</b> {user.get('diamonds', 0):,}\n\n"
        f"🎮 <b>O'yinlar:</b> {played}\n"
        f"🏆 <b>G'alabalar:</b> {won}\n"
        f"❌ <b>Mag'lubiyatlar:</b> {lost}\n"
        f"🔥 <b>Win Rate:</b> {win_rate}%\n"
        f"🌟 <b>MVP soni:</b> {user.get('mvp_count', 0)}\n"
        f"💀 <b>Chiqarilganlar:</b> {user.get('eliminations_count', 0)}\n"
        f"{sep}\n"
        f"🏅 <b>Yutuqlar ({len(achievements)}):</b>\n{ach_text}\n"
        f"{sep}"
    )
