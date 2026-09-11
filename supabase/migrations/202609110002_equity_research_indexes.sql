create index if not exists stock_candidates_run_id_idx on trading_bot.stock_candidates(run_id);
create index if not exists positions_candidate_id_idx on trading_bot.positions(candidate_id);
create index if not exists position_alerts_position_id_idx on trading_bot.position_alerts(position_id);
