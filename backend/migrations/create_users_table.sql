create table if not exists public.users (
    id uuid default uuid_generate_v4() primary key,
    email text unique not null,
    name text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    last_sign_in timestamp with time zone,
    credentials jsonb
);

-- Create indexes
create index if not exists users_email_idx on public.users (email); 