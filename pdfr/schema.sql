drop table if exists documents;
create table documents (
  id integer primary key autoincrement,
  title string not null,
  user string not null,
  source string not null,
  published string not null,
  timestamp datetime not null,
  link string,
  comment string
);
