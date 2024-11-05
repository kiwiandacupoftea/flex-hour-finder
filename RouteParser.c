#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE_LENGTH 100

typedef struct {
    char tlh[6]; // time to leave home and go to work
    int dh2w; // duration travel home to work
    char taw[6]; // time to arrive at work
    char tlw[6]; // time to leave work and go home
    int dw2h; // duration travel work to home
    char tsw[6]; // desired time to start 8-hour workday
} Route;

void printRoutes(Route* r, int count) {
    for (int i = 0; i < count; i++) {
        printf("Route %d - Starting At %s\n",i,r[i].tsw);
        printf("Time To Leave Home: %s\n",r[i].tlh);
        printf("Duration To Work: %d\n",r[i].dh2w);
        printf("Time To Arrive At Work: %s\n",r[i].taw);
        printf("Time To Leave Work: %s\n",r[i].tlw);
        printf("Duration To Home: %d\n",r[i].dw2h);
    }
}

int time_in_minutes(const char* time) {
    int hrs, mins;
    if (sscanf(time, "%2d:%2d", &hrs, &mins) != 2) {
        fprintf(stderr, "Invalid time format: %s\n", time);
        return -1;
    }

    return hrs * 60 + mins;
}

int main(int argc, char* argv[]) {

    if (argc != 2) {
        fprintf(stderr, "Invalid number of arguments. Usage: .\\RouteParser.exe <path_of_csv>");
        return 1;
    }

    FILE* fptr = fopen(argv[1], "r");

    if (fptr == NULL) {
        fprintf(stderr, "Invalid file path. Usage: .\\RouteParser.exe <path_of_csv>");
        return 2;
    }

    char line[MAX_LINE_LENGTH];
    Route* routes = NULL; 
    int count = 0;

    while(fgets(line, MAX_LINE_LENGTH, fptr)) {
        char t1[6]; // time to leave starting location
        int n;      // duration of travel to destination
        char t2[6]; // time to arrive at destination
        char t3[6]; // intended arrival/departure time
        char c;     // either 's' for start time or 'e' for end time marker

        // parse the travel data
        if (sscanf(line, "%5[^,],%d,%5[^,],%5[^,],%c", t1, &n, t2, t3, &c) == 5) {

            // if travel is for a start time, either allocate new Route or compare to previous
            if (c == 's') {
                // compare to current Routes, change flag if updated
                int updated = 0;
                for (int i = 0; i < count; i++) {
                    // update the Route if the marker is the same
                    int cur_marker = time_in_minutes(t3);
                    int r_marker = time_in_minutes(routes[i].tsw);
                    if (cur_marker == r_marker) {
                        strcpy(routes[i].tlh, t1);
                        routes[i].dh2w = n;
                        strcpy(routes[i].taw, t2);
                        strcpy(routes[i].tsw, t3);
                        // set the flag
                        updated = 1;
                    }
                }
                // if Route was not updated, add a new one
                if (updated == 0) {
                    // attempt to allocate memory for new Route
                    Route* temp = realloc(routes, (count + 1) * sizeof(Route));
                    if (temp == NULL) {
                        fprintf(stderr, "Memory reallocation failed\n");
                        free(routes);
                        fclose(fptr);
                        return 3;
                    }
                    routes = temp;
                    // zero-initialize the newly allocated Route
                    memset(&routes[count], 0, sizeof(Route));
                    // store variables in Route object
                    strcpy(routes[count].tlh, t1);
                    routes[count].dh2w = n;
                    strcpy(routes[count].taw, t2);
                    strcpy(routes[count].tsw, t3);
                    // update count for Routes array
                    count++;
                }                              
            }
            else if (c == 'e') {
                // update Route with corresponding start time
                for (int i = 0; i < count; i ++) {
                    int cur_marker = time_in_minutes(t3);
                    // find end marker by adding 8 hrs (480 minutes) to start marker
                    int r_marker = time_in_minutes(routes[i].tsw) + 480;
                    if (cur_marker == r_marker) {
                        // update Route with travel going home
                        strcpy(routes[i].tlw, t1);
                        routes[i].dw2h = n;
                    }
                }
            }
        } 
        else {
            fprintf(stderr, "Error parsing line: %s", line);
        }
    }
    // close the file
    fclose(fptr);

    // print contents of array
    //printRoutes(routes, count);

    // find best route, set flag if found
    int route_found = 0;
    if (count > 0) {
        Route* best_route = NULL;
        // find route with shortest travel time
        for (int i = 0; i < count; i++) {
            // check Route has a round trip travel time
            if (routes[i].dh2w != 0 && routes[i].dw2h != 0) {
                int cur_total = routes[i].dh2w + routes[i].dw2h;
                // make best Route if one doesnt exist
                if (best_route == NULL) {
                    best_route = &routes[i];
                }
                else {
                    int best_total = best_route->dh2w + best_route->dw2h;
                    // give preference to Route that starts at a later time
                    if (cur_total <= best_total) {
                        best_route = &routes[i];
                    }
                }
            }
        }

        if (best_route != NULL) {
            printf("Best route: %s start time, ~%dmin to work, ~%dmin home, approx. round trip of %d minutes\n", 
                best_route->tsw, best_route->dh2w, best_route->dw2h, best_route->dh2w + best_route->dw2h);
            route_found = 1;
        }
    }

    // print message if route not found
    if (!route_found) {
        printf("Route not found.\n");
    }

    // deallocate memory for array
    free(routes);

    return 0;
}