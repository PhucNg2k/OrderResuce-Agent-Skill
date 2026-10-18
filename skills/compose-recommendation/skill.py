from runtime.models import Decision, PipelineState

RUNS_WHEN_HALTED = True

HEADLINES = {
    "CLARIFY": "Đề xuất hỏi người mua một câu (tin nhắn giả lập)",
    "STANDARD_RETRY": "Đề xuất giao lại theo quy trình bình thường, chờ đội vận hành xác nhận",
    "HOLD": "Đề xuất tạm giữ đơn và đánh giá lại sau",
    "NO_ACTION": "Đang chờ người mua trả lời, chưa làm gì thêm",
    "HUMAN_REVIEW": "Chuyển cho đội vận hành xem xét",
    "CLOSE": "Đơn đã giao, đóng case",
}

CAUSES = {
    "TEMPORARY_ABSENCE": "người mua vắng mặt tạm thời",
    "UNKNOWN_CONTACT_PROBLEM": "chưa liên lạc được, chưa rõ lý do",
    "UNCLEAR_LOCATION": "địa chỉ / mốc nhận biết chưa rõ",
    "DISRUPTION": "gián đoạn dịch vụ tại khu vực giao",
    "UNVERIFIED_REFUSAL": "trạng thái 'từ chối' chưa được xác minh",
    "UNKNOWN": "chưa xác định",
}

REASONS = {
    "already_delivered": "Đơn đã giao thành công.",
    "policy_version_mismatch": "Phiên bản luật của case khác với luật đang dùng.",
    "return_in_progress": "Đơn đã bắt đầu hoàn về, ý định của người mua không thay đổi được việc này.",
    "return_state_unknown": "Chưa rõ trạng thái hoàn hàng.",
    "deadline_unknown": "Chưa rõ hạn xử lý.",
    "deadline_expired": "Đã quá hạn xử lý.",
    "attempts_exhausted": "Đã hết lượt giao (giá trị giả lập).",
    "model_unavailable": "Không gọi được AI. Cần người xử lý.",
    "model_refused_or_empty": "AI không trả kết quả. Cần người xử lý.",
    "invalid_model_output": "Kết quả AI sai định dạng. Cần người xử lý.",
    "replay_missing": "Không có kết quả AI đã lưu cho tình huống này.",
    "replay_version_mismatch": "Kết quả AI đã lưu thuộc phiên bản prompt/luật khác.",
    "invalid_evidence_reference": "AI dẫn chứng một bằng chứng không tồn tại.",
    "unsupported_claim": "AI đưa ra nhận định không khớp với bằng chứng.",
    "missing_question_key": "AI đề xuất hỏi nhưng không chọn câu hỏi được duyệt.",
    "prohibited_wording": "Kết quả AI có câu chữ bị cấm (đổ lỗi hoặc hứa hẹn).",
    "conflicting_evidence": "Các bằng chứng mâu thuẫn nhau.",
    "refusal_unverified": "Trạng thái 'từ chối' không có bằng chứng đi kèm. Không tự hoàn hàng, không đánh dấu người mua.",
    "no_reply_after_question": "Đã hỏi nhưng hết thời gian chờ mà không có trả lời. Không coi đây là từ chối.",
    "waiting_for_reply": "Đã hỏi người mua, đang trong thời gian chờ trả lời.",
    "question_limit_reached": "Đã dùng hết số câu hỏi cho phép mà case vẫn chưa rõ.",
    "buyer_not_contactable": "Không liên lạc được người mua.",
    "question_not_approved": "Câu hỏi không nằm trong mẫu được duyệt.",
    "no_active_disruption": "Không có gián đoạn đang diễn ra để tạm giữ.",
    "no_open_response_window": "Không có câu hỏi nào đang chờ trả lời.",
    "handoff_proposed": "Cần người có thẩm quyền xử lý tiếp.",
    "retry_blocked:confidence_not_high": "Chưa đủ bằng chứng để giao lại.",
    "retry_blocked:cause_not_retryable": "Nguyên nhân này không được giao lại tự động.",
    "retry_blocked:disruption_active": "Khu vực vẫn đang gián đoạn.",
    "retry_blocked:location_unclear": "Địa chỉ chưa rõ.",
}

BLOCKED = {
    "EDIT_ADDRESS": "đổi địa chỉ",
    "PROMISE_DELIVERY_TIME": "hứa giờ giao cụ thể",
    "DISPATCH_COURIER": "điều phối shipper",
    "AUTO_RETURN": "tự hoàn hàng",
    "AUTO_REFUND": "tự hoàn tiền",
    "AUTO_CANCEL": "tự hủy đơn",
    "PENALIZE_BUYER": "đánh dấu / phạt người mua",
    "SEND_REAL_MESSAGE": "gửi tin nhắn thật",
    "CALL_CARRIER_API": "gọi hệ thống thật của hãng vận chuyển",
}

NEXT_OWNER = {
    "CLARIFY": "buyer_reply_pending",
    "NO_ACTION": "buyer_reply_pending",
    "HOLD": "system_reassess",
    "STANDARD_RETRY": "operations",
    "HUMAN_REVIEW": "operations",
    "CLOSE": "none",
}


def reason_text(code: str) -> str:
    if code.startswith("blocked_action:"):
        action = code.split(":", 1)[1]
        return f"Hành động '{BLOCKED.get(action, action)}' luôn bị chặn trong prototype. Đã chuyển cho đội vận hành."
    return REASONS.get(code, code)


def run(state: PipelineState) -> PipelineState:
    gate, a, r = state.gate, state.assessment, state.run
    question_key = a.question_key if a and gate.action == "CLARIFY" else None
    question_text = state.policy["question_templates"].get(question_key) if question_key else None

    lines = [HEADLINES[gate.action]]
    if a:
        lines.append(f"Nguyên nhân có khả năng: {CAUSES[a.cause]} · Mức chắc chắn: {a.confidence}")
    if question_text:
        lines.append(f"Câu hỏi: \"{question_text}\"")
    lines += [f"- {reason_text(c)}" for c in gate.reasons]
    if gate.reassess_at:
        lines.append(f"Đánh giá lại lúc: {gate.reassess_at.strftime('%H:%M %d/%m')}")

    mode_label = "REPLAY · output AI đã lưu" if state.mode == "REPLAY" else "LIVE_AI"
    state.decision = Decision(
        decision_id=f"{r.run_id}:{state.trigger}",
        run_id=r.run_id,
        case_id=r.case.case_id,
        trigger=state.trigger,
        decided_at=r.now,
        status=gate.status,
        action=gate.action,
        cause=a.cause if a else None,
        confidence=a.confidence if a else None,
        rescue_potential=a.rescue_potential if a else None,
        evidence_ids=(a.supporting_evidence_ids + a.conflicting_evidence_ids) if a else [],
        question_key=question_key,
        question_text=question_text,
        reasons=gate.reasons,
        blocked_actions=gate.blocked_actions,
        message_vi="\n".join(lines),
        next_owner=NEXT_OWNER[gate.action],
        reassess_at=gate.reassess_at,
        model_info=state.model_info,
        model_explanation=a.explanation if a else None,
        policy_version=state.policy["policy_version"],
        labels=["Dữ liệu giả lập", "Luật minh họa", "Kết quả mô phỏng", mode_label],
    )
    return state
