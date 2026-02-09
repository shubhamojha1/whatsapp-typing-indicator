/**
 * Cross-platform keystroke detector
 * 
 * Outputs to stdout:
 *   KEY:<char>   - when a regular key is pressed
 *   ENTER        - when Enter is pressed
 *   BACKSPACE    - when Backspace is pressed
 *   EXIT         - when Ctrl+C or EOF is detected
 * 
 * Compile:
 *   Windows: g++ -o keystroke_detector.exe keystroke_detector.cpp
 *   Linux:   g++ -o keystroke_detector keystroke_detector.cpp
 */

#include <iostream>
#include <cstdlib>
#include <cstdio>

#ifdef _WIN32
    // Windows-specific headers
    #include <conio.h>
    #include <windows.h>
#else
    // Unix/Linux/Mac headers
    #include <termios.h>
    #include <unistd.h>
    #include <fcntl.h>
    // #include <csignal>
#endif

// Disable output buffering for real-time communication
void disable_buffering() {
    std::cout.setf(std::ios::unitbuf);
    setvbuf(stdout, nullptr, _IONBF, 0);
}

#ifdef _WIN32
// ============ WINDOWS IMPLEMENTATION ============

// static HANDLE g_hStdin = INVALID_HANDLE_VALUE;
// static DWORD g_originalMode = 0;

// static BOOL WINAPI console_ctrl_handler(DWORD ctrl_type) {
//     if (ctrl_type == CTRL_C_EVENT || ctrl_type == CTRL_BREAK_EVENT) {
//         if (g_hStdin != INVALID_HANDLE_VALUE && g_originalMode != 0) {
//             SetConsoleMode(g_hStdin, g_originalMode);
//         }
//     }
//     return FALSE;
// }

int get_char() {
    if (_kbhit()) {
        return _getch();
    }
    return -1;
}

void run_detector() {
    // g_hStdin = GetStdHandle(STD_INPUT_HANDLE);
    // if (g_hStdin != INVALID_HANDLE_VALUE) {
    //     GetConsoleMode(g_hStdin, &g_originalMode);
    //     SetConsoleCtrlHandler(console_ctrl_handler, TRUE);
    // }

    while (true) {
        int ch = get_char();
        
        if (ch == -1) {
            // No key pressed, small sleep to avoid CPU spinning
            Sleep(10);
            continue;
        }
        
        if (ch == 3) {  // Ctrl+C
            // if (g_hStdin != INVALID_HANDLE_VALUE && g_originalMode != 0) {
            //     SetConsoleMode(g_hStdin, g_originalMode);
            // }
            std::cout << "EXIT" << std::endl;
            break;
        } else if (ch == 13 || ch == 10) {  // Enter
            std::cout << "ENTER" << std::endl;
        } else if (ch == 8 || ch == 127) {  // Backspace
            std::cout << "BACKSPACE" << std::endl;
        } else if(ch == 32) {
            std::cout << "SPACE" << std::endl;
        }
         else if (ch >= 32 && ch <= 126) {  // Printable ASCII
            std::cout << "KEY:" << static_cast<char>(ch) << std::endl;
        }
        // Ignore other special keys (arrows, function keys, etc.)
    }
    // if (g_hStdin != INVALID_HANDLE_VALUE) {
    //     SetConsoleCtrlHandler(console_ctrl_handler, FALSE);
    // }
}

#else
// ============ UNIX/LINUX/MAC IMPLEMENTATION ============

struct termios original_termios;

void restore_terminal() {
    tcsetattr(STDIN_FILENO, TCSANOW, &original_termios);
}

void enable_raw_mode() {
    tcgetattr(STDIN_FILENO, &original_termios);
    atexit(restore_terminal);
    
    struct termios raw = original_termios;
    // Disable canonical mode (line buffering) and echo
    raw.c_lflag &= ~(ICANON | ECHO);
    // Set minimum characters for read and timeout
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 1;  // 100ms timeout
    
    tcsetattr(STDIN_FILENO, TCSANOW, &raw);
}

int get_char() {
    char ch;
    int nread = read(STDIN_FILENO, &ch, 1);
    if (nread == 1) {
        return static_cast<unsigned char>(ch);
    }
    return -1;
}

void run_detector() {
    enable_raw_mode();
    
    while (true) {
        int ch = get_char();
        
        if (ch == -1) {
            continue;
        }
        
        if (ch == 3 || ch == 4) {  // Ctrl+C or Ctrl+D
            std::cout << "EXIT" << std::endl;
            break;
        } else if (ch == 13 || ch == 10) {  // Enter
            std::cout << "ENTER" << std::endl;
        } else if (ch == 127 || ch == 8) {  // Backspace
            std::cout << "BACKSPACE" << std::endl;
        } else if (ch >= 32 && ch <= 126) {  // Printable ASCII
            std::cout << "KEY**:" << static_cast<char>(ch) << std::endl;
        }
        // Ignore escape sequences (arrow keys, etc.) for simplicity
    }
}

#endif

int main() {
    std::cout << "=== NEW BUILD ===\n";
    disable_buffering();
    run_detector();
    return 0;
}
