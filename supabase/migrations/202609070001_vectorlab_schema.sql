-- Isolated from existing application tables. This schema is not exposed through
-- Supabase's Data API unless explicitly added to the project's exposed schemas.
create schema if not exists trading_bot;
create table trading_bot.workspaces (id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade, name text not null, created_at timestamptz not null default now());
create table trading_bot.automation_runs (id uuid primary key default gen_random_uuid(), workspace_id uuid not null references trading_bot.workspaces(id) on delete cascade, state text not null check(state in ('stopped','running','paused','completed','failed')), mode text not null check(mode='paper'), strategy_version text not null, created_at timestamptz not null default now());
create table trading_bot.paper_fills (id uuid primary key default gen_random_uuid(), workspace_id uuid not null references trading_bot.workspaces(id) on delete cascade, run_id uuid references trading_bot.automation_runs(id) on delete set null, occurred_at timestamptz not null, symbol text not null, side text not null check(side in ('buy','sell')), quantity numeric not null check(quantity>0), price numeric not null check(price>0), commission numeric not null default 0 check(commission>=0));
create table trading_bot.market_quotes (id bigint generated always as identity primary key, workspace_id uuid not null references trading_bot.workspaces(id) on delete cascade, symbol text not null, price numeric not null check(price>0), as_of timestamptz not null, provider text not null, delayed boolean not null default false, received_at timestamptz not null default now());
create index market_quotes_workspace_symbol_asof_idx on trading_bot.market_quotes(workspace_id,symbol,as_of desc);
create index workspaces_user_id_idx on trading_bot.workspaces(user_id);
create index automation_runs_workspace_id_idx on trading_bot.automation_runs(workspace_id);
create index paper_fills_workspace_id_idx on trading_bot.paper_fills(workspace_id);
create index paper_fills_run_id_idx on trading_bot.paper_fills(run_id);
alter table trading_bot.workspaces enable row level security; alter table trading_bot.automation_runs enable row level security; alter table trading_bot.paper_fills enable row level security; alter table trading_bot.market_quotes enable row level security;
create policy "workspace owner" on trading_bot.workspaces for all to authenticated using((select auth.uid())=user_id) with check((select auth.uid())=user_id);
create policy "owner reads runs" on trading_bot.automation_runs for select to authenticated using(exists(select 1 from trading_bot.workspaces w where w.id=workspace_id and w.user_id=(select auth.uid())));
create policy "owner reads fills" on trading_bot.paper_fills for select to authenticated using(exists(select 1 from trading_bot.workspaces w where w.id=workspace_id and w.user_id=(select auth.uid())));
create policy "owner reads quotes" on trading_bot.market_quotes for select to authenticated using(exists(select 1 from trading_bot.workspaces w where w.id=workspace_id and w.user_id=(select auth.uid())));
grant usage on schema trading_bot to authenticated;
grant select,insert,update,delete on trading_bot.workspaces,trading_bot.automation_runs,trading_bot.paper_fills,trading_bot.market_quotes to authenticated;
