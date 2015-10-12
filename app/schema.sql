drop table if exists messages;
create table messages (
    chat integer not null,
    sender integer not null,
    recver integer not null,
    text text not null,
    time integer not null
);
drop table if exists chats;
create table chats (
    chat integer not null unique,
    full integer
);
