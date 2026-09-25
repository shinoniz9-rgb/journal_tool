"""
Trade Calculations and Performance Analytics Utilities
"""
from typing import List, Dict, Any, Tuple


def calculate_trade_metrics(
    trade_type: str,
    entry_price: float,
    exit_price: float | None,
    stop_loss: float | None,
    take_profit: float | None,
    position_size: float = 0.0,
    leverage: int = 1,
    fees: float = 0.0,
    risk_amount: float = 0.0
) -> Dict[str, float]:
    """
    Tính toán PnL, ROI %, Planned R:R, Realized R:R cho một lệnh giao dịch.
    Hỗ trợ cơ chế Risk-Based (tính theo số tiền stoploss rủi ro $).
    """
    metrics = {
        "pnl": 0.0,
        "pnl_percent": 0.0,
        "planned_rr": 0.0,
        "realized_rr": 0.0,
    }

    if entry_price <= 0:
        return metrics

    is_long = trade_type.strip().lower() == "long"

    # 1. Tính Planned R:R (Nếu có SL và TP)
    risk_distance = 0.0
    if stop_loss and stop_loss > 0:
        if is_long:
            risk_distance = entry_price - stop_loss
        else:
            risk_distance = stop_loss - entry_price

    if risk_distance > 0 and take_profit and take_profit > 0:
        reward_distance = (take_profit - entry_price) if is_long else (entry_price - take_profit)
        if reward_distance > 0:
            metrics["planned_rr"] = round(reward_distance / risk_distance, 2)

    # 2. Tính PnL và Realized R:R (Nếu lệnh đã có giá đóng exit_price)
    if exit_price and exit_price > 0:
        # Tính Realized R:R nếu có khoảng cách SL hợp lệ
        if risk_distance > 0:
            realized_diff = (exit_price - entry_price) if is_long else (entry_price - exit_price)
            metrics["realized_rr"] = round(realized_diff / risk_distance, 2)

        # CƠ CHẾ 1: TÍNH THEO SỐ TIỀN RỦI RO STOPLOSS (RISK AMOUNT $)
        # "khi đặt entry và giá stoploss thì sẽ mất số tiền bao nhiêu đó, lãi lỗ tp cũng tính từ số tiền mất cho stoploss để tính"
        if risk_amount and risk_amount > 0 and risk_distance > 0:
            realized_diff = (exit_price - entry_price) if is_long else (entry_price - exit_price)
            realized_r = realized_diff / risk_distance
            raw_pnl = realized_r * risk_amount
            net_pnl = raw_pnl - fees
            metrics["pnl"] = round(net_pnl, 2)
            metrics["pnl_percent"] = round((net_pnl / risk_amount) * 100, 2)
        else:
            # CƠ CHẾ 2: DỰ PHÒNG THEO POSITION SIZE & ĐÒN BẨY
            effective_pos = position_size if position_size > 0 else 100.0
            if is_long:
                price_change_ratio = (exit_price - entry_price) / entry_price
            else:
                price_change_ratio = (entry_price - exit_price) / entry_price
            raw_pnl = price_change_ratio * (effective_pos * leverage)
            net_pnl = raw_pnl - fees
            metrics["pnl"] = round(net_pnl, 2)
            metrics["pnl_percent"] = round((net_pnl / effective_pos) * 100, 2)

    return metrics


def calculate_portfolio_statistics(trades: List[Dict[str, Any]], initial_capital: float = 1000.0) -> Dict[str, Any]:
    """
    Tổng hợp toàn diện các chỉ số thống kê hiệu suất giao dịch (KPIs)
    kèm theo số vốn ban đầu và vốn hiện tại sau lãi / lỗ.
    """
    total_trades = len(trades)
    closed_trades = [t for t in trades if t.get("status") == "Closed"]
    open_trades = [t for t in trades if t.get("status") == "Open"]

    if not closed_trades:
        return {
            "initial_capital": round(initial_capital, 2),
            "current_capital": round(initial_capital, 2),
            "capital_growth_percent": 0.0,
            "total_trades": total_trades,
            "closed_trades_count": 0,
            "open_trades_count": len(open_trades),
            "win_trades": 0,
            "loss_trades": 0,
            "breakeven_trades": 0,
            "win_rate": 0.0,
            "net_pnl": 0.0,
            "gross_pnl": 0.0,
            "total_fees": 0.0,
            "total_profit": 0.0,
            "total_loss": 0.0,
            "profit_factor": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "avg_rr": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "equity_curve": [],
            "strategy_stats": {},
            "emotion_stats": {},
            "symbol_stats": {},
        }

    # Phân loại thắng / thua / hòa
    win_list = [t for t in closed_trades if (t.get("pnl") or 0) > 0]
    loss_list = [t for t in closed_trades if (t.get("pnl") or 0) < 0]
    be_list = [t for t in closed_trades if (t.get("pnl") or 0) == 0]

    win_count = len(win_list)
    loss_count = len(loss_list)
    be_count = len(be_list)
    total_closed = len(closed_trades)

    win_rate = round((win_count / total_closed) * 100, 1) if total_closed > 0 else 0.0

    total_profit = sum(t.get("pnl") or 0 for t in win_list)
    total_loss = abs(sum(t.get("pnl") or 0 for t in loss_list))
    net_pnl = round(total_profit - total_loss, 2)
    total_fees = round(sum(float(t.get("fees") or 0.0) for t in closed_trades), 2)
    gross_pnl = round(net_pnl + total_fees, 2)

    profit_factor = (
        round(total_profit / total_loss, 2)
        if total_loss > 0
        else (None if total_profit > 0 else 0.0)
    )

    avg_win = round(total_profit / win_count, 2) if win_count > 0 else 0.0
    avg_loss = round(total_loss / loss_count, 2) if loss_count > 0 else 0.0

    # R:R trung bình của các lệnh có dữ liệu
    rr_values = [t.get("realized_rr") for t in closed_trades if t.get("realized_rr") is not None]
    avg_rr = round(sum(rr_values) / len(rr_values), 2) if rr_values else 0.0

    pnl_values = [t.get("pnl") or 0 for t in closed_trades]
    best_trade = max(pnl_values) if pnl_values else 0.0
    worst_trade = min(pnl_values) if pnl_values else 0.0

    # Tính chuỗi thắng / thua liên tiếp lớn nhất (dựa trên thứ tự thời gian)
    # Sắp xếp lệnh theo ngày thoát / ngày vào
    sorted_trades = sorted(
        closed_trades,
        key=lambda x: (x.get("exit_date") or x.get("entry_date") or x.get("id") or 0)
    )

    max_wins = 0
    curr_wins = 0
    max_losses = 0
    curr_losses = 0

    cumulative_pnl = 0.0
    equity_curve: List[Tuple[str, float]] = []

    for t in sorted_trades:
        pnl = t.get("pnl") or 0.0
        cumulative_pnl += pnl
        label_date = t.get("exit_date") or t.get("entry_date") or f"Lệnh #{t.get('id')}"
        # Lấy ngày ngắn gọn
        if len(str(label_date)) >= 10:
            label_date = str(label_date)[:10]
        equity_curve.append((str(label_date), round(cumulative_pnl, 2)))

        if pnl > 0:
            curr_wins += 1
            curr_losses = 0
            if curr_wins > max_wins:
                max_wins = curr_wins
        elif pnl < 0:
            curr_losses += 1
            curr_wins = 0
            if curr_losses > max_losses:
                max_losses = curr_losses
        else:
            curr_wins = 0
            curr_losses = 0

    # Thống kê theo Chiến lược (Strategy)
    strategy_stats: Dict[str, Dict[str, Any]] = {}
    for t in closed_trades:
        strat = t.get("strategy") or "Không rõ"
        if strat not in strategy_stats:
            strategy_stats[strat] = {"count": 0, "wins": 0, "pnl": 0.0}
        strategy_stats[strat]["count"] += 1
        pnl = t.get("pnl") or 0.0
        strategy_stats[strat]["pnl"] += pnl
        if pnl > 0:
            strategy_stats[strat]["wins"] += 1

    for strat, data in strategy_stats.items():
        data["win_rate"] = round((data["wins"] / data["count"]) * 100, 1) if data["count"] > 0 else 0.0
        data["pnl"] = round(data["pnl"], 2)

    # Thống kê theo Tâm lý (Emotion)
    emotion_stats: Dict[str, Dict[str, Any]] = {}
    for t in closed_trades:
        emo = t.get("emotion") or "Không rõ"
        if emo not in emotion_stats:
            emotion_stats[emo] = {"count": 0, "wins": 0, "pnl": 0.0}
        emotion_stats[emo]["count"] += 1
        pnl = t.get("pnl") or 0.0
        emotion_stats[emo]["pnl"] += pnl
        if pnl > 0:
            emotion_stats[emo]["wins"] += 1

    for emo, data in emotion_stats.items():
        data["win_rate"] = round((data["wins"] / data["count"]) * 100, 1) if data["count"] > 0 else 0.0
        data["pnl"] = round(data["pnl"], 2)

    # Thống kê theo Cặp coin (Symbol)
    symbol_stats: Dict[str, Dict[str, Any]] = {}
    for t in closed_trades:
        sym = t.get("symbol") or "Khác"
        if sym not in symbol_stats:
            symbol_stats[sym] = {"count": 0, "wins": 0, "pnl": 0.0}
        symbol_stats[sym]["count"] += 1
        pnl = t.get("pnl") or 0.0
        symbol_stats[sym]["pnl"] += pnl
        if pnl > 0:
            symbol_stats[sym]["wins"] += 1

    for sym, data in symbol_stats.items():
        data["win_rate"] = round((data["wins"] / data["count"]) * 100, 1) if data["count"] > 0 else 0.0
    current_capital = round(initial_capital + net_pnl, 2)
    capital_growth_percent = round(((net_pnl) / initial_capital) * 100, 2) if initial_capital > 0 else 0.0

    return {
        "initial_capital": round(initial_capital, 2),
        "current_capital": current_capital,
        "capital_growth_percent": capital_growth_percent,
        "total_trades": total_trades,
        "closed_trades_count": total_closed,
        "open_trades_count": len(open_trades),
        "win_trades": win_count,
        "loss_trades": loss_count,
        "breakeven_trades": be_count,
        "win_rate": win_rate,
        "net_pnl": net_pnl,
        "gross_pnl": gross_pnl,
        "total_fees": total_fees,
        "total_profit": round(total_profit, 2),
        "total_loss": round(total_loss, 2),
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "avg_rr": avg_rr,
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2),
        "max_consecutive_wins": max_wins,
        "max_consecutive_losses": max_losses,
        "equity_curve": equity_curve,
        "strategy_stats": strategy_stats,
        "emotion_stats": emotion_stats,
        "symbol_stats": symbol_stats,
    }
