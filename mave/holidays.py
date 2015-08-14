from datetime import date

holidays = {
  'USFederal': set([
    date(2000, 1, 17),
    date(2000, 2, 21),
    date(2000, 5, 29),
    date(2000, 7, 4),
    date(2000, 9, 4),
    date(2000, 10, 9),
    date(2000, 11, 10),
    date(2000, 11, 23),
    date(2000, 12, 25),
    date(2001, 1, 1),
    date(2001, 1, 15),
    date(2001, 2, 19),
    date(2001, 5, 28),
    date(2001, 7, 4),
    date(2001, 9, 3),
    date(2001, 10, 8),
    date(2001, 11, 12),
    date(2001, 11, 22),
    date(2001, 12, 25),
    date(2002, 1, 1),
    date(2002, 1, 21),
    date(2002, 2, 18),
    date(2002, 5, 27),
    date(2002, 7, 4),
    date(2002, 9, 2),
    date(2002, 10, 14),
    date(2002, 11, 11),
    date(2002, 11, 28),
    date(2002, 12, 25),
    date(2003, 1, 1),
    date(2003, 1, 20),
    date(2003, 2, 17),
    date(2003, 5, 26),
    date(2003, 7, 4),
    date(2003, 9, 1),
    date(2003, 10, 13),
    date(2003, 11, 11),
    date(2003, 11, 27),
    date(2003, 12, 25),
    date(2004, 1, 1),
    date(2004, 1, 19),
    date(2004, 2, 16),
    date(2004, 5, 31),
    date(2004, 7, 5),
    date(2004, 9, 6),
    date(2004, 10, 11),
    date(2004, 11, 11),
    date(2004, 11, 25),
    date(2004, 12, 24),
    date(2005, 1, 17),
    date(2005, 2, 21),
    date(2005, 5, 30),
    date(2005, 7, 4),
    date(2005, 9, 5),
    date(2005, 10, 10),
    date(2005, 11, 11),
    date(2005, 11, 24),
    date(2005, 12, 26),
    date(2006, 1, 2),
    date(2006, 1, 16),
    date(2006, 2, 20),
    date(2006, 5, 29),
    date(2006, 7, 4),
    date(2006, 9, 4),
    date(2006, 10, 9),
    date(2006, 11, 10),
    date(2006, 11, 23),
    date(2006, 12, 25),
    date(2007, 1, 1),
    date(2007, 1, 15),
    date(2007, 2, 19),
    date(2007, 5, 28),
    date(2007, 7, 4),
    date(2007, 9, 3),
    date(2007, 10, 8),
    date(2007, 11, 12),
    date(2007, 11, 22),
    date(2007, 12, 25),
    date(2008, 1, 1),
    date(2008, 1, 21),
    date(2008, 2, 18),
    date(2008, 5, 26),
    date(2008, 7, 4),
    date(2008, 9, 1),
    date(2008, 10, 13),
    date(2008, 11, 11),
    date(2008, 11, 27),
    date(2008, 12, 25),
    date(2009, 1, 1),
    date(2009, 1, 19),
    date(2009, 2, 16),
    date(2009, 5, 25),
    date(2009, 7, 3),
    date(2009, 9, 7),
    date(2009, 10, 12),
    date(2009, 11, 11),
    date(2009, 11, 26),
    date(2009, 12, 25),
    date(2010, 1, 1),
    date(2010, 1, 18),
    date(2010, 2, 15),
    date(2010, 5, 31),
    date(2010, 7, 5),
    date(2010, 9, 6),
    date(2010, 10, 11),
    date(2010, 11, 11),
    date(2010, 11, 25),
    date(2010, 12, 24),
    date(2011, 1, 17),
    date(2011, 2, 21),
    date(2011, 5, 30),
    date(2011, 7, 4),
    date(2011, 9, 5),
    date(2011, 10, 10),
    date(2011, 11, 11),
    date(2011, 11, 24),
    date(2011, 12, 26),
    date(2012, 1, 2),
    date(2012, 1, 16),
    date(2012, 2, 20),
    date(2012, 5, 28),
    date(2012, 7, 4),
    date(2012, 9, 3),
    date(2012, 10, 8),
    date(2012, 11, 12),
    date(2012, 11, 22),
    date(2012, 12, 25),
    date(2013, 1, 1),
    date(2013, 1, 21),
    date(2013, 2, 18),
    date(2013, 5, 27),
    date(2013, 7, 4),
    date(2013, 9, 2),
    date(2013, 10, 14),
    date(2013, 11, 11),
    date(2013, 11, 28),
    date(2013, 12, 25),
    date(2014, 1, 1),
    date(2014, 1, 20),
    date(2014, 2, 17),
    date(2014, 5, 26),
    date(2014, 7, 4),
    date(2014, 9, 1),
    date(2014, 10, 13),
    date(2014, 11, 11),
    date(2014, 11, 27),
    date(2014, 12, 25),
    date(2015, 1, 1),
    date(2015, 1, 19),
    date(2015, 2, 16),
    date(2015, 5, 25),
    date(2015, 7, 3),
    date(2015, 9, 7),
    date(2015, 10, 12),
    date(2015, 11, 11),
    date(2015, 11, 26),
    date(2015, 12, 25)
  ]),
  'GoodFriday': set([
    date(2000, 4, 21),
    date(2001, 4, 13),
    date(2002, 3, 29),
    date(2003, 4, 18),
    date(2004, 4, 9),
    date(2005, 3, 25),
    date(2006, 4, 14),
    date(2007, 4, 6),
    date(2008, 3, 21),
    date(2009, 4, 10),
    date(2010, 4, 2),
    date(2011, 4, 22),
    date(2012, 4, 6),
    date(2013, 3, 29),
    date(2014, 4, 18),
    date(2015, 4, 3)
  ]),
}
