## Title

[OC] Every nuclear test since 1945, mapped: 2,055 explosions by eight countries, 178 in 1962 alone, and 84% of all the explosive yield was set off on islands

## Body

I mapped every nuclear test in the SIPRI list of nuclear explosions (Bergkvist and Ferm 2000, 1945 to 1998) plus North Korea's six tests from 2006 to 2017: 2,055 tests, not counting Hiroshima and Nagasaki. Circles are sized by the cube root of yield, the way blast damage scales. Testing peaked at 178 tests in 1962, one every two days, after a pause from 1958 to 1961. After the 1963 Partial Test Ban Treaty 95% of tests were underground, but France and China kept testing in the atmosphere until 1974 and 1980. The total yield was about 546 megatons (range 429 to 664); Novaya Zemlya alone took 51%, and islands 84%, though they saw only 21% of tests. Every French and British test was outside the home country, in Algeria, French Polynesia, Australia, the central Pacific and Nevada. Caveats: yields are estimates, often only "less than" some figure, so I use the middle of each range; counts differ between sources depending on how salvoes are counted. Interactive map with a year slider and a filter for atmospheric and underground tests: https://maps.tristanhotham.com/nuclear-tests/

## Source comment

Sources: Bergkvist, N.-O. and Ferm, R. (2000) Nuclear Explosions 1945 to 1998, FOA and SIPRI, via data is plural (https://github.com/data-is-plural/nuclear-explosions) and TidyTuesday 2019-08-20 (credit Jesus Castagnetto); Wikipedia, List of nuclear weapons tests of North Korea and List of nuclear weapons tests (CC BY-SA 4.0); Natural Earth outlines (public domain).

Tools: Python (pandas, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/nuclear-tests/
Paper: https://doi.org/{10.5281/zenodo.23857489}
Blog post: {https://blog.tristanhotham.com/2026/10/31/nuclear-tests/}
