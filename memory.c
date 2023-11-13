// gcc memory.c -o memory -Wall -Wextra -Wvla && ./memory

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/random.h>

#define NB_CARDS 20
#define SIZE_CARDS 85

void pack_of_cards(char cards[NB_CARDS][SIZE_CARDS]);

typedef struct { int x, y; } couple;

typedef struct {
    int nb_player;
    int* score_players;
    int i_player;
    int nb_rows;
    int nb_columns;
    int** board;
    couple* cards_found;
    int nb_cards_found;
} memory;

void shuffle(int* l, int length) {
    for (int i = 0; i < length; i++) {
        int rand = random() % length;
        int temp = l[rand];
        l[rand] = l[i];
        l[i]  = temp;
    }
}

memory generate_memory() {
    int nb_player=0, nb_rows=0, nb_columns=0, board_size;

    while (nb_player < 1) { printf("Choose number of players (>0) : "); scanf("%d", &nb_player); }
    int* score_players = (int*)malloc(sizeof(int)*nb_player);
    for (int i=0; i<nb_player; i++) score_players[i] = 0;

    while (nb_rows < 1 || nb_rows > NB_CARDS/2) { printf("Choose number of rows ⟦1; %d⟧ : ", NB_CARDS/2); scanf("%d", &nb_rows); }
    while (nb_columns < 1 || nb_columns > NB_CARDS/nb_rows) { printf("Choose number of columns ⟦1;%d⟧ : ", NB_CARDS/nb_rows); scanf("%d", &nb_columns); }
    if (nb_rows%2 != 0 || nb_columns%2 != 0) {
        nb_columns++;
        printf("Number of columns increased by 1 for an even number of cards\n\n");
    }
    board_size = nb_columns*nb_rows;

    int** board = (int**)malloc(sizeof(int*)*nb_rows);
    int* values_cards = (int*)malloc(sizeof(int)*board_size);
    for (int i=0; i<board_size/2; i++) { values_cards[i*2]=i; values_cards[i*2+1]=i; }
    shuffle(values_cards, board_size);
    for (int i=0; i<nb_rows; i++) {
        board[i] = (int*)malloc(sizeof(int)*nb_columns);
        for (int j=0; j<nb_columns; j++) board[i][j] = values_cards[i*(nb_rows+1)+j];
    }
    free(values_cards);
    couple* cards_found = (couple*)malloc(sizeof(couple)*board_size);

    memory memory = {nb_player, score_players, 0, nb_rows, nb_columns, board, cards_found, 0};

    return memory;
}

int card_is_found(int i, int j, couple* cards_found, int nb_cards_found) {
    for (int c=0; c<nb_cards_found; c++) if (i == cards_found[c].x && j == cards_found[c].y) return 1;
    return 0;
}

void show_memory(memory memory) {
    for (int i=0; i<memory.nb_rows; i++) {
        for (int j=0; j<memory.nb_columns; j++) printf("╶───╴");
        printf("\n");
        for (int j=0; j<memory.nb_columns; j++) {
            if (card_is_found(i, j, memory.cards_found, memory.nb_cards_found) == 1) printf("│XXX│");
            else printf("│%d,%d│", i, j);
        }
        printf("\n");
        for (int j=0; j<memory.nb_columns; j++) printf("╶───╴");
        printf("\n");
    }
}

void choose_card(memory* memory, char cards[NB_CARDS][SIZE_CARDS]) {
    printf("Player %d must play\n", memory->i_player);
    int i1=-1, i2=-1, j1=-1, j2=-1;
    while (i1 < 0 || j1 < 0 || i1 >= memory->nb_rows || j1 >= memory->nb_columns || card_is_found(i1, j1, memory->cards_found, memory->nb_cards_found) == 1) {
        printf("Choose 1st card (i,j) : "); scanf("%d,%d", &i1,&j1);
    }
    int card1 = memory->board[i1][j1];
    printf("%s\n", cards[card1]);

    while (i2 < 0 || j2 < 0 || i2 >= memory->nb_rows || j2 >= memory->nb_columns || (i2 == i1 && j2 == j1) || card_is_found(i2, j2, memory->cards_found, memory->nb_cards_found) == 1) {
        printf("Choose 2nd card (i,j) : "); scanf("%d,%d", &i2,&j2);
    }
    int card2 = memory->board[i2][j2];
    printf("%s\n", cards[card2]);

    if (card1 == card2) {
        memory->score_players[memory->i_player]++;
        couple c1 = {i1,j1};
        memory->cards_found[memory->nb_cards_found] = c1;
        couple c2 = {i2,j2};
        memory->cards_found[memory->nb_cards_found+1] = c2;
        memory->nb_cards_found += 2;
        printf("You found a pair\n");
    } else {
        memory->i_player = (memory->i_player+1)%memory->nb_player;
        printf("You didn't find a pair\n");
    }
}

void best_player(memory memory) {
    int i_best_player = 0;
    int score_best_player = memory.score_players[i_best_player];
    for (int i=1; i<memory.nb_player; i++) {
        if (memory.score_players[i] > score_best_player) {
            score_best_player = memory.score_players[i];
            i_best_player = i;
        }
    }

    printf("The best player is the player %d with %d points !!!\n", i_best_player, score_best_player);
}

int main() {
    char cards[NB_CARDS][SIZE_CARDS]; pack_of_cards(cards);

    char play = 'Y';
    while (play == 'Y') {
        memory memory = generate_memory();

        while (memory.nb_cards_found < memory.nb_rows*memory.nb_columns) {
            show_memory(memory);
            choose_card(&memory, cards);
            printf("\n");
        }
        printf("\nEnd of game !!!\n");

        best_player(memory);

        free(memory.score_players);
        for (int i=0; i<memory.nb_rows; i++) free(memory.board[i]);
        free(memory.board);

        printf("Play again ? (Y/N) : "); scanf(" %c", &play);
    }

   return 0;
}

void pack_of_cards(char cards[NB_CARDS][SIZE_CARDS]) {
    strncpy(cards[0], " _____\n|2    |\n|  v  |\n|     |\n|  v  |\n|____Z|", SIZE_CARDS);
    strncpy(cards[1], " _____\n|3    |\n| v v |\n|     |\n|  v  |\n|____E|", SIZE_CARDS);
    strncpy(cards[2], "^__^\n(oo)\\_______\n(__)\\       )\\/\n    ||----w |\n    ||     ||", SIZE_CARDS);
    strncpy(cards[3], "      /\\\n     /  \\\n    /`'.,\\\n   /     ',\n  /      ,`\\\n /   ,.'`.  \\\n/.,'`     `'.\\", SIZE_CARDS);
    strncpy(cards[4], " .-.\n(o o) boo!\n| O \\\n \\   \\\n  `~~~'", SIZE_CARDS);
    for (int i=5; i<NB_CARDS; i++) { strncpy(cards[i], "Card i", SIZE_CARDS); cards[i][5] = i+'0'; }
}