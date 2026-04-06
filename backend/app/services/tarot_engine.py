from typing import List, Dict, Any

class TarotLogicEngine:
    """
    Tầng xử lý nghiệp vụ Tarot (Occult Rules):
    Xử lý Tương sinh tương khắc nguyên tố (Elemental Dignities) 
    và Năng lượng đảo ngược (Reversals).
    """

    def analyze_elemental_dignities(self, cards: List[Dict[str, Any]]) -> str:
        """
        Phân tích sự tương tác của nguyên tố giữa các lá bài trong trải bài.
        """
        elements = [c.get("element", "").lower() for c in cards if c.get("element")]
        if not elements:
            return ""

        counts = {
            "fire": elements.count("fire"),
            "water": elements.count("water"),
            "air": elements.count("air"),
            "earth": elements.count("earth"),
        }

        total = sum(counts.values())
        if total == 0:
            return ""

        analysis = []
        
        # Check predominant element
        for elem, count in counts.items():
            if count >= total / 2 and total > 1:
                if elem == "fire":
                    analysis.append("- Yếu tố Lửa (Đam mê, Hành động, Ý chí) đang thống trị trải bài.")
                elif elem == "water":
                    analysis.append("- Yếu tố Nước (Cảm xúc, Trực giác, Các mối quan hệ) đang thống trị trải bài.")
                elif elem == "air":
                    analysis.append("- Yếu tố Khí (Lý trí, Suy nghĩ, Giao tiếp) đang thống trị trải bài.")
                elif elem == "earth":
                    analysis.append("- Yếu tố Đất (Thực tế, Vật chất, Sự ổn định) đang thống trị trải bài.")

        # Check missing element
        missing = [e for e, c in counts.items() if c == 0]
        if len(missing) == 1:
            m = missing[0]
            if m == "fire":
                analysis.append("- Thiếu hụt Lửa: Sự việc đang thiếu động lực, thiếu nhiệt huyết hoặc sự dứt khoát.")
            elif m == "water":
                analysis.append("- Thiếu hụt Nước: Thiếu đi sự gắn kết cảm xúc, sự đồng cảm hoặc trực giác.")
            elif m == "air":
                analysis.append("- Thiếu hụt Khí: Cần thêm sự giao tiếp rõ ràng, logic và khách quan.")
            elif m == "earth":
                analysis.append("- Thiếu hụt Đất: Thiếu đi nền tảng vững chắc, tính thực tế hoặc hành động cụ thể.")

        # Elemental clashes
        if counts["fire"] > 0 and counts["water"] > 0:
            analysis.append("- Xung đột Lửa - Nước: Có sự mâu thuẫn giữa lý trí/đam mê và cảm xúc (chúng làm suy yếu lẫn nhau).")
        if counts["air"] > 0 and counts["earth"] > 0:
            analysis.append("- Xung đột Khí - Đất: Có sự mâu thuẫn giữa lý tưởng bay bổng và thực tế cồng kềnh.")

        # Elemental supports
        if counts["fire"] > 0 and counts["air"] > 0:
            analysis.append("- Tương trợ Lửa - Khí: Tư duy (Khí) đang thổi bùng khao khát và hành động (Lửa). Năng lượng rất mạnh mẽ.")
        if counts["water"] > 0 and counts["earth"] > 0:
            analysis.append("- Tương trợ Nước - Đất: Cảm xúc (Nước) đang nuôi dưỡng nền tảng thực tế (Đất). Một sự kết hợp rất vững chắc.")

        return "\n".join(analysis)

    def process_reversals_and_context(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Gắn nhãn rõ ràng hơn cho lá bài dựa trên is_reversed
        """
        processed_cards = []
        for c in cards:
            c_copy = dict(c)
            is_rev = bool(c_copy.get("is_reversed", False))
            
            # Gán rõ ràng nghĩa đang active
            if is_rev:
                c_copy["active_meaning"] = c_copy.get("meaning_reversed") or c_copy.get("meaning_upright")
                c_copy["energy_state"] = "Năng lượng đang bị nghẽn, thái quá, hoặc hướng vào trong (Reversed)."
            else:
                c_copy["active_meaning"] = c_copy.get("meaning_upright")
                c_copy["energy_state"] = "Năng lượng tỏa ra thuận lợi, tự nhiên (Upright)."
                
            processed_cards.append(c_copy)
            
        return processed_cards

    def build_system_context(self, cards: List[Dict[str, Any]]) -> str:
        """
        Xâu chuỗi thành một khối Context hoàn chỉnh để nạp cho RAG Master Prompt.
        """
        dignities = self.analyze_elemental_dignities(cards)
        context = ""
        if dignities:
            context += "[PHÂN TÍCH TƯƠNG QUAN NGUYÊN TỐ - ELEMENTAL DIGNITIES]\n"
            context += dignities + "\n\n"
            
        # Thêm đếm Major Arcana vs Minor
        majors = [c for c in cards if str(c.get("arcana")).lower() in ["major", "major arcana", "trưởng"]]
        if len(majors) >= max(2, len(cards) / 2):
            context += "[PHÂN TÍCH ARCANA]\n"
            context += f"- Có {len(majors)}/{len(cards)} lá Major Arcana: Trải bài này nói về những bài học nghiệp quả lớn, những sự kiện định mệnh khó tránh khỏi, không chỉ là chuyện vặt vãnh hàng ngày.\n"
            
        return context
