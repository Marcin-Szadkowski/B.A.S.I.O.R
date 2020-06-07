Mapper tool was created for purposes of B.A.S.I.O.R project to 
define tramline communication loops and check behaviuor of graph when deleting edges.


Mapper creates two json files. One edges.json contains edges do delete.
Second file tram_loops.json contains tram loops.

Mapper gets clicks on map from user and write them to files.After that application
updates graphml object (Wroclaw tram graph) and presents how it looks like 
after deletion. Loops after submit are shown in blue .

Usage:
===================================================================
To delete edge run pplication, check apriopriate checkbox and choose
coordinates by clicking on map. After submit data is appended to file.
Application based on choices finds the nearest graph edges and deletes them with
osmnx,networkx  methods. Updated graph is shown in real time after submit.
If you want to clear json file type "clear" in upper textfield, if u want to clear 
edges.json file or lower textbox, if u want to clear tram_loops.json.

To to show loops is important to click even number of times, because 
loops are made by touples of 2 edges. After collecting loops data in textfield
click submit. After a while application will update tramline graph real time with loops 
shown in blue. During process of collecting loops, edges for a loops are not 
deleted from graph so that graph structure does not change. If you want to
stop showing loops type in lower textfield "stop", then application will
return base graph without color features.s
