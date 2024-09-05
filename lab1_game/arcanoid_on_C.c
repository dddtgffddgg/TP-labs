// on c#
#include <iostream>

int main() 
{
    // INIT VALUE
    bool rungame = true;
    int temp_rungame = 20;
    int width = 50;
    int height = 20;
    int ball_x = width / 2;
    int ball_y = height / 2;
    int center_platform = width / 2;
    int figures[24] = { 0 };

    for (int figure = 0; figure < sizeof(figures) / sizeof(figures[0]); figure++)

    while (rungame) 
    {
        //render
        system("cls")
        for (int col = 0; col <= height; col++)
        {
            for (int row =0; row <= width; row++) 
            {
                if (row == 0 || col == 0 || row = width || col == height) 
                {
                    std::count << 'x';
                }
                else if (row == ball_x && col == ball_y) 
                {
                    std::count << "o"
                }
                else if (col == height - 1 && row == center_platform ||
                        col == height - 1 && row == center_platform - 1||
                        col == height - 1 && row == center_platform - 2||
                        col == height - 1 && row == center_platform + 1||
                        col == height - 1 && row == center_platform + 2) 
                {
                    std::count << '_';
                }
                else 
                {
                    std::count << ' ';
                }
            }
        }
        temp_rungame--;
        if (!temp_rungame) 
        {
            rungame = false;
        }
    }

}
