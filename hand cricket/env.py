import cv2
import mediapipe as mp
import random
import numpy as np
import time

class HandCricket:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        self.player_score = 0
        self.computer_score = 0
        self.batting = True
        self.last_computer_number = 0
        self.frame_count = 0
        self.update_interval = 30  # Update computer's number every 30 frames
        self.game_state = "READY"  # Possible states: READY, PLAYING, OUT
        self.out_start_time = 0
        
    def get_finger_count(self, hand_landmarks):
        """Improved logic to count fingers"""
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky tips
        finger_bases = [6, 10, 14, 18]  # Base joints of the fingers
        thumb_tip = 4
        thumb_base = 2
        count = 0
        
        # Special check for thumb (for 6)
        thumb_tip_y = hand_landmarks.landmark[thumb_tip].y
        thumb_base_y = hand_landmarks.landmark[thumb_base].y
        
        # If thumb is pointing upwards (for 6)
        if thumb_tip_y < thumb_base_y:
            all_fingers_down = True
            for tip, base in zip(finger_tips, finger_bases):
                if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
                    all_fingers_down = False
                    break
            if all_fingers_down:
                return 6
        
        # Normal counting for 1-5
        for tip, base in zip(finger_tips, finger_bases):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
                count += 1
                
        return count

    def draw_game_info(self, img, player_number):
        # Game status bar
        cv2.rectangle(img, (0, 0), (640, 50), (0, 0, 0), -1)
        status = "Batting" if self.batting else "Bowling"
        cv2.putText(img, f"Status: {status}", (10, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Scoreboard
        cv2.rectangle(img, (10, 60), (300, 240), (255, 255, 255), 2)
        cv2.putText(img, f"Player: {player_number}", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, f"Computer: {self.last_computer_number}", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, f"Player Score: {self.player_score}", (20, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, f"Computer Score: {self.computer_score}", (20, 220), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def play_game(self):
        while True:
            success, img = self.cap.read()
            if not success:
                print("Failed to get frame from camera!")
                break

            img = cv2.flip(img, 1)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_img)
            
            self.frame_count += 1
            player_number = 0

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    player_number = self.get_finger_count(hand_landmarks)

                    if self.frame_count >= self.update_interval:
                        self.last_computer_number = random.randint(1, 6)
                        self.frame_count = 0

                        if self.game_state == "READY":
                            if self.batting:
                                if player_number == self.last_computer_number:
                                    self.game_state = "OUT"
                                    self.out_start_time = time.time()
                                else:
                                    self.player_score += player_number
                            else:
                                if player_number == self.last_computer_number:
                                    self.game_state = "GAME_OVER"
                                else:
                                    self.computer_score += self.last_computer_number

            # Game state management
            if self.game_state == "OUT":
                cv2.putText(img, "OUT!", (250, 300), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                if time.time() - self.out_start_time > 2:
                    self.batting = False
                    self.game_state = "READY"

            elif self.game_state == "GAME_OVER":
                cv2.putText(img, "GAME OVER!", (200, 300), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                if time.time() - self.out_start_time > 2:
                    break

            self.draw_game_info(img, player_number)
            
            cv2.namedWindow("Hand Cricket", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Hand Cricket", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow("Hand Cricket", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Final result screen after game ends
        result_img = np.zeros((600, 800, 3), np.uint8)
        
        # Gradient background
        for i in range(600):
            result_img[i] = [i//3, 40, 100]
        
        # Header
        cv2.putText(result_img, "*** GAME OVER ***", (200, 100), 
                   cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255), 2)
        
        # Winner declaration
        if self.player_score > self.computer_score:
            message = "*** PLAYER WINS! ***"
            symbol = "<<< WINNER >>>"
            color = (0, 255, 0)
        elif self.player_score < self.computer_score:
            message = "Computer Wins!"
            symbol = "GAME OVER"
            color = (0, 0, 255)
        else:
            message = "IT'S A TIE!"
            symbol = "= = ="
            color = (255, 255, 0)
        
        # Scorecard box
        cv2.rectangle(result_img, (150, 150), (650, 450), (255, 255, 255), 2)
        cv2.rectangle(result_img, (150, 150), (650, 200), color, -1)
        
        # Winner message
        cv2.putText(result_img, message, (200, 190), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # Large symbol
        cv2.putText(result_img, symbol, (250, 300), 
                   cv2.FONT_HERSHEY_TRIPLEX, 2, (255, 255, 255), 2)
        
        # Display scores
        cv2.putText(result_img, f"Player Score: {self.player_score}", (200, 380), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(result_img, f"Computer Score: {self.computer_score}", (200, 420), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Decorative lines
        cv2.line(result_img, (200, 450), (600, 450), color, 2)
        cv2.line(result_img, (200, 455), (600, 455), (255, 255, 255), 1)
        
        # Footer
        cv2.putText(result_img, "Press any key to exit", (300, 550), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
        
        cv2.namedWindow("Game Result", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Game Result", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Game Result", result_img)

        cv2.waitKey(0)
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = HandCricket()
    game.play_game()
