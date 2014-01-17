drop table if exists photos;
create table photos (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);
