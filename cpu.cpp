#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <stdio.h>
#include <stdlib.h>
#include <iomanip>
#include <iostream>

#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>

#include "Goals/KillOpponent.h"
#include "Goals/NavigateMenu.h"

#include "Gamestate.h"

void PrintState(GameState* state)
{
    std::cout << "p1 percent: " << state->player_one_percent << std::endl;
    std::cout << "p2 percent: " << state->player_two_percent << std::endl;
    std::cout << "p1 stock: " << state->player_one_stock << std::endl;
    std::cout << "p2 stock: " << state->player_two_stock << std::endl;
    if(state->player_one_facing)
    {
        std::cout << "p1 facing: right" << std::endl;
    }
    else
    {
        std::cout << "p1 facing: left" << std::endl;

    }
    if(state->player_two_facing)
    {
        std::cout << "p2 facing: right" << std::endl;
    }
    else
    {
        std::cout << "p2 facing: left" << std::endl;
    }
    std::cout << "frame: " << state->frame << std::endl;
    std::cout << "menu state: " << state->menu_state << std::endl;
    std::cout << "p2 pointer x: " << state->player_two_pointer_x << std::endl;
    std::cout << "p2 pointer y: " << state->player_two_pointer_y << std::endl;

    std::cout << "p1 x: " << std::fixed << std::setprecision(10) << state->player_one_x << std::endl;
    std::cout << "p1 y: " << std::fixed << std::setprecision(10) << state->player_one_y << std::endl;

    std::cout << "p2 x: " << std::fixed << std::setprecision(10) << state->player_two_x << std::endl;
    std::cout << "p2 y: " << std::fixed << std::setprecision(10) << state->player_two_y << std::endl;

    std::cout << "p1 action: " << std::hex << state->player_one_action << std::endl;
    std::cout << "p2 action: " << std::hex << state->player_two_action << std::endl;

    std::cout << "p1 action count: " << std::dec << state->player_one_action_counter << std::endl;
    std::cout << "p2 action count: " << std::dec << state->player_two_action_counter << std::endl;

    std::cout << "p1 action frame: " << std::dec << state->player_one_action_frame << std::endl;
    std::cout << "p2 action frame: " << std::dec << state->player_two_action_frame << std::endl;

    if(state->player_one_invulnerable)
    {
        std::cout << "p1 invulnerable" << std::endl;
    }
    else
    {
        std::cout << "p1 not invulnerable" << std::endl;
    }
    if(state->player_two_invulnerable)
    {
        std::cout << "p2 invulnerable" << std::endl;
    }
    else
    {
        std::cout << "p2 not invulnerable" << std::endl;
    }

    std::cout << "p1 hitlag frames left: " << state->player_one_hitlag_frames_left << std::endl;
    std::cout << "p2 hitlag frames left: " << state->player_two_hitlag_frames_left << std::endl;

    std::cout << "p1 hitstun frames left: " << state->player_one_hitstun_frames_left << std::endl;
    std::cout << "p2 hitstun frames left: " << state->player_two_hitstun_frames_left << std::endl;

    std::cout << "p1 jumps left: " << state->player_one_jumps_left << std::endl;
    std::cout << "p2 jumps left: " << state->player_two_jumps_left << std::endl;

    if(state->player_one_on_ground)
    {
        std::cout << "p1 on ground" << std::endl;
    }
    else
    {
        std::cout << "p1 in air" << std::endl;
    }
    if(state->player_two_on_ground)
    {
        std::cout << "p2 on ground" << std::endl;
    }
    else
    {
        std::cout << "p2 in air" << std::endl;
    }

    std::cout << "p1 speed x air self: " << state->player_one_speed_air_x_self << std::endl;
    std::cout << "p2 speed x air self: " << state->player_two_speed_air_x_self << std::endl;

    std::cout << "p1 speed y self: " << state->player_one_speed_y_self << std::endl;
    std::cout << "p2 speed y self: " << state->player_two_speed_y_self << std::endl;

    std::cout << "p1 speed x attack: " << state->player_one_speed_x_attack << std::endl;
    std::cout << "p2 speed x attack: " << state->player_two_speed_x_attack << std::endl;

    std::cout << "p1 speed y attack: " << state->player_one_speed_y_attack << std::endl;
    std::cout << "p2 speed y attack: " << state->player_two_speed_y_attack << std::endl;

    std::cout << "p1 speed x ground self: " << state->player_one_speed_ground_x_self << std::endl;
    std::cout << "p2 speed x ground self: " << state->player_two_speed_ground_x_self << std::endl;
}

int main()
{
    int shmid;
    key_t key;
    char *shm;
    GameState *state;

	//return 0;
    key = 1337;

    /*
     * Locate the segment.
     */
    if ((shmid = shmget(key, sizeof(GameState), 0666)) < 0) {
        perror("shmget");
        exit(1);
    }

    /*
     * Now we attach the segment to our data space.
     */
    if ((shm = (char*)shmat(shmid, NULL, 0)) == (char *) -1) {
        perror("shmat");
        exit(1);
    }

    state = (GameState*)shm;

    PrintState(state);

    uint last_frame = state->frame;
    //Get our goal
	Goal *goal = NULL;
    MENU current_menu = (MENU)state->menu_state;

    //Main frame loop
    for(;;)
    {
        //Spinloop until we get a new frame
        if(state->frame != last_frame)
        {
            if(state->frame > last_frame+1)
            {
                std::cout << "WARNING: FRAME MISSED" << std::endl;
            }
            last_frame = state->frame;

            //If we're in a match, play the match!
            if(state->menu_state == IN_GAME)
            {
                if(goal == NULL )
                {
                    goal = new KillOpponent(state);
                }
                if(typeid(*goal) != typeid(KillOpponent))
                {
                    delete goal;
                    goal = new KillOpponent(state);
                }
                goal->Strategize();
            }
            //If we're in a menu, then let's navigate the menu
            else if(state->menu_state == CHARACTER_SELECT ||
                state->menu_state == STAGE_SELECT ||
                state->menu_state == POSTGAME_SCORES)
            {
                if(goal == NULL )
                {
                    goal = new NavigateMenu(state);
                }
                if(typeid(*goal) != typeid(NavigateMenu))
                {
                    delete goal;
                    goal = new NavigateMenu(state);
                }
                goal->Strategize();
            }
        }
        //If the menu changed
        else if(current_menu != state->menu_state)
        {
            last_frame = 1;
            current_menu = (MENU)state->menu_state;
        }
    }

	return EXIT_SUCCESS;
}
