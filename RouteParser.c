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

int main(int argc, char* argv[]) {

    if (argc != 2) {
        printf("Invalid number of arguments. Usage: .\\RouteParser.exe <path_of_csv>");
        return 1;
    }

    FILE* fptr = fopen(argv[1], "r");

    if (fptr == NULL) {
        printf("Invalid file path. Usage: .\\RouteParser.exe <path_of_csv>");
        return 1;
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

            // add new Route to array if a start time
            if (c == 's') {
                // allocate memory for new Route
                routes = realloc(routes, (count + 1) * sizeof(Route));
                if (routes == NULL) {
                    perror("Memory allocation failed");
                    fclose(fptr);
                    return 1;
                }

                // zero-initialize the newly allocated Route
                memset(&routes[count], 0, sizeof(Route));

                // store variables in Route object
                strcpy(routes[count].tlh, t1);
                routes[count].dh2w = n;
                strcpy(routes[count].taw, t2);
                strcpy(routes[count].tsw, t3);
            }

            count++;
        } else {
            fprintf(stderr, "Error parsing line: %s", line);
        }
    }

    fclose(fptr);

    // print contents of array
    printRoutes(routes, count);

    // deallocate memory for array
    free(routes);

    return 0;
}