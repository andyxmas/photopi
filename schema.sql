drop table if exists photos;
create table photos (
  id integer primary key autoincrement,
  filename text,
  date datetime,
  title text,
  text text
);
