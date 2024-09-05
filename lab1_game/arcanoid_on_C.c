// on c#
#include <iostream>

int main() 
{
    // INIT VALUE
    bool rungame = true;
    int temp_rungame = 20;
    int width = 50;
    int height = 20;

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
