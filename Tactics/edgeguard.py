import melee
import globals
import Chains
import math
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Tactics.punish import Punish
from Tactics.defend import Defend
from Chains.dropdownshine import Dropdownshine

class Edgeguard(Tactic):
    def __init__(self):
        self.upbstart = 0

    # This is exactly flipped from the recover logic
    def canedgeguard():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        if not smashbot_state.off_stage and opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return True

        if not opponent_state.off_stage:
            return False

        # We can now assume that opponent is off the stage...

        # If smashbot is on stage
        if not smashbot_state.off_stage:
            return True

        # If smashbot is in hitstun, then recover
        if smashbot_state.off_stage and smashbot_state.hitstun_frames_left > 0:
            return True

        # If smashbot is closer to the edge, edgeguard
        diff_x_opponent = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(opponent_state.x))
        diff_x = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        opponent_dist = math.sqrt( opponent_state.y**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( smashbot_state.y**2 + (diff_x)**2 )

        if smashbot_dist < opponent_dist:
            return True

        return False

    def upbheight():
        character = globals.opponent_state.character
        if character == Character.FOX:
            return 84.55
        if character == Character.FALCO:
            return 62.4
        if character == Character.CPTFALCON:
            return 37.62
        if character == Character.MARTH:
            return 50.72
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            return 54.39
        if character == Character.JIGGLYPUFF:
            return 0
        if character == Character.PEACH:
            return 28.96
        if character == Character.ZELDA:
            return 70.412
        if character == Character.SHEIK:
            return 69.632
        if character == Character.SAMUS:
            return 46.1019

        # This is maybe average, in case we get here
        return 40

    def upbapexframes():
        character = globals.opponent_state.character
        if character == Character.FOX:
            return 118
        if character == Character.FALCO:
            return 70
        if character == Character.CPTFALCON:
            return 45
        if character == Character.MARTH:
            return 23
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            return 30
        if character == Character.JIGGLYPUFF:
            return 0
        if character == Character.PEACH:
            return 34
        if character == Character.ZELDA:
            return 73
        # Sheik's up-b is dumb, and has TWO points where it can grab the edge. Ugh
        #   This just counts the first
        if character == Character.SHEIK:
            return 19
        if character == Character.SAMUS:
            return 38

        # This is maybe average, in case we get here
        return 40

    # This is the very lazy way of doing this, but "meh". Maybe I'll get around to doing it right
    def isupb():
        character = globals.opponent_state.character
        action = globals.opponent_state.action
        if character in [Character.FOX, Character.FALCO]:
            if action in [Action.SWORD_DANCE_3_LOW, Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_1_AIR]:
                return True
        if character == Character.CPTFALCON:
            if action in [Action.SWORD_DANCE_3_LOW]:
                return True
        if character == Character.MARTH:
            if action in [Action.SHINE_RELEASE_AIR]:
                return True
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            if action in [Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_4_LOW, Action.SWORD_DANCE_1_AIR]:
                return True
        if character == Character.JIGGLYPUFF:
            return False
        if character == Character.PEACH:
            if action in [Action.SWORD_DANCE_3_LOW_AIR]:
                return True
        if character == Character.ZELDA:
            if action in [Action.SWORD_DANCE_3_HIGH, Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW]:
                return True
        if character == Character.SHEIK:
            if action in [Action.SWORD_DANCE_1_AIR, Action.SWORD_DANCE_2_HIGH_AIR, Action.SWORD_DANCE_2_MID_AIR]:
                return True
        if character == Character.SAMUS:
            if action in [Action.SWORD_DANCE_3_LOW]:
                return True
        return False

    def snaptoedgeframes():
        # How long will it take opponent to grab the edge?
        #   Distance to the snap point of the edge
        opponent_state = globals.opponent_state
        edge_x = melee.stages.edgegroundposition(globals.gamestate.stage)
        edgedistance = abs(opponent_state.x) - (edge_x + 10)
        # Assume opponent can move at their "max" speed
        airhorizspeed = globals.framedata.characterdata[opponent_state.character]["AirSpeed"]
        edgegrabframes_x = edgedistance // airhorizspeed
        fastfallspeed = globals.framedata.characterdata[opponent_state.character]["FastFallSpeed"]

        # Can opponent get to the vertical snap position in time?
        #   This is the shortest possible time opponent could get into position
        edgegrabframes_y = 1000
        # Are they already in place?
        if -5 > opponent_state.y > -18:
            edgegrabframes_y = 0
        # Are they above?
        elif opponent_state.y > -5:
            edgegrabframes_y = (opponent_state.y + 5) // fastfallspeed
        # Are they below?
        elif opponent_state.y < -18:
            # TODO: Capture nuances of when they are in jump and not
            djapexframes = globals.framedata.getdjapexframes(opponent_state)
            djheight = globals.framedata.getdjheight(opponent_state)
            # Can they double-jump to grab the edge?
            if -5 > opponent_state.y + djheight > -18:
                edgegrabframes_y = djapexframes
            elif opponent_state.y + djheight > -5:
                # If the jump puts them too high, then we have to wait for them to fall after the jump
                fallframes = (opponent_state.y + djheight + 5) // fastfallspeed
                edgegrabframes_y = djapexframes + fallframes
            elif opponent_state.y + djheight < -18:
                # If the jump puts them too low, then they have to UP-B. How long will that take?
                upbframes = Edgeguard.upbapexframes()
                edgegrabframes_y = upbframes
                # How many falling frames do they need?
                fallframes = (opponent_state.y + upbframes + 5) // fastfallspeed
                if fallframes > 0:
                    edgegrabframes_y += fallframes

        edgegrabframes = max(edgegrabframes_x, edgegrabframes_y)

        # TODO: Teleport exception here
        #edgegrabframes = TELEPORT

        return edgegrabframes

    def step(self):
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        if Dropdownshine.inrange():
            self.pickchain(Chains.Dropdownshine)
            return

        if smashbot_state.action == Action.EDGE_CATCHING:
            self.pickchain(Chains.Nothing)
            return

        # How many frames will it take to get to our opponent right now?
        onedge = smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        # Stand up if opponent attacks us
        proj_incoming = Defend.needsprojectiledefense() and smashbot_state.invulnerability_left <= 2

        hitframe = globals.framedata.inrange(opponent_state, smashbot_state, globals.gamestate.stage)
        framesleft = hitframe - opponent_state.action_frame
        if proj_incoming or (hitframe != 0 and onedge and framesleft < 5):
            # Unless the attack is a grab, then don't bother
            if not globals.framedata.isgrab(opponent_state.character, opponent_state.action):
                if Edgeguard.isupb():
                    #TODO: Make this a chain
                    self.chain = None
                    globals.controller.press_button(Button.BUTTON_L)
                    return
                else:
                    self.chain = None
                    self.pickchain(Chains.DI, [0.5, 0.65])
                    return

        # Special exception for Fox/Falco illusion
        #   Since it is dumb and technically a projectile
        if opponent_state.character in [Character.FOX, Character.FALCO]:
            if opponent_state.action in [Action.SWORD_DANCE_2_MID]:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            if opponent_state.action in [Action.SWORD_DANCE_4_MID]:
                #TODO: Make this a chain
                self.chain = None
                globals.controller.press_button(Button.BUTTON_L)
                return

        # What recovery options does opponent have?
        landonstage = False
        grabedge = False
        # they have to commit to an up-b to recover
        mustupb = False
        canrecover = True

        djheight = globals.framedata.getdjheight(opponent_state)

        edgegrabframes = Edgeguard.snaptoedgeframes()

        # How heigh can they go with a jump?
        potentialheight = djheight + opponent_state.y
        if potentialheight < -18:
            mustupb = True

        # Now consider UP-B
        #   Have they already UP-B'd?
        if Edgeguard.isupb():
            if self.upbstart == 0:
                self.upbstart = opponent_state.y
            # If they are halfway through the up-b, then subtract out what they've alrady used
            potentialheight = Edgeguard.upbheight() + self.upbstart
        elif opponent_state.action == Action.DEAD_FALL:
            potentialheight = opponent_state.y
        else:
            potentialheight += Edgeguard.upbheight()

        if potentialheight > 0:
            landonstage = True
        if potentialheight > -18:
            grabedge = True
        if potentialheight < -18:
            mustupb = True
            canrecover = False


        # Split the logic into two:
        #   A) We are on the edge
        #   B) We are on the stage

        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            # If opponent can't recover, then just get onto the stage!
            if not canrecover:
                #TODO: Make this a chain
                self.chain = None
                globals.controller.press_button(Button.BUTTON_L)
                return

            # Roll up to edgehog
            if Edgeguard.isupb() and potentialheight < 0 and opponent_state.character == Character.MARTH:
                #TODO: Make this a chain
                self.chain = None
                globals.controller.press_button(Button.BUTTON_L)
                return

            isillusion = opponent_state.action in [Action.SWORD_DANCE_2_HIGH, Action.SWORD_DANCE_2_MID] and \
                opponent_state.character in [Character.FOX, Character.FALCO]

            # Edgestall
            #   We must be on the first frame, or else it's dangerous
            if not isillusion and smashbot_state.action == Action.EDGE_HANGING and smashbot_state.invulnerability_left >= 17:
                if edgegrabframes > 29:
                    self.pickchain(Chains.Edgestall)
                    return

            # Shine them!
            #   We are in danger of being attacked!
            #   It's unsafe to be in shine range of opponent. We can't react to the attack!
            if globals.gamestate.distance < 11.8 and smashbot_state.invulnerability_left == 0 and \
                    opponent_state.character in [Character.FOX, Character.FALCO, Character.JIGGLYPUFF]:
                if opponent_state.speed_y_self > 0 and globals.difficulty >= 3:
                    self.pickchain(Chains.Dropdownshine)
                    return
                else:
                    self.chain = None
                    self.pickchain(Chains.DI, [0.5, 0.65])
                    return

            # Do nothing
            self.chain = None
            self.pickchain(Chains.Nothing)
            return

        # We are on the stage
        else:
            # Can we challenge their ledge?
            framesleft = Punish.framesleft()
            if not onedge and opponent_state.invulnerability_left < 5:
                if globals.difficulty >= 3 or framesleft > 10:
                    self.pickchain(Chains.Grabedge)
                    return

            # Dash dance near the edge
            edge_x = melee.stages.edgegroundposition(globals.gamestate.stage)
            pivotpoint = opponent_state.x
            # Don't run off the stage though, adjust this back inwards a little if it's off
            edgebuffer = 10
            pivotpoint = min(pivotpoint, edge_x - edgebuffer)
            pivotpoint = max(pivotpoint, (-edge_x) + edgebuffer)

            self.chain = None
            self.pickchain(Chains.DashDance, [pivotpoint])