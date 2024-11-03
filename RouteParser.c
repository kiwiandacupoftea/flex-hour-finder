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
} Route;

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
        char t1[6];
        int n; 
        char t2[6]; 

        // parse the travel data
        if (sscanf(line, "%5[^,],%d,%5[^,\n]", t1, &n, t2) == 3) {

            routes = realloc(routes, (count + 1) * sizeof(Route));
            if (routes == NULL) {
                perror("Memory allocation failed");
                fclose(fptr);
                return 1;
            }

            // store variables in Route object
            strcpy(routes[count].tlh, t1);
            routes[count].dh2w = n;
            strcpy(routes[count].taw, t2);

            count++;
        } else {
            fprintf(stderr, "Error parsing line: %s", line);
        }
    }

    fclose(fptr);

    // print contents of array
    for (int i = 0; i < count; i++) {
        printf("%d | Start Time: %s | Number: %d | End Time: %s\n", i, routes[i].tlh, routes[i].dh2w, routes[i].taw);
    }

    // deallocate memory for array
    free(routes);

    return 0;
}