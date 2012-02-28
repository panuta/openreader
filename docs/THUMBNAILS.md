Create a thumbnail for DOC, XLS, PPT, ODT
==========================================

1. Install OpenOffice headless package

    ```
    $ sudo apt-get install openoffice.org-headless openoffice.org-java-common openoffice.org-writer openoffice.org-calc openoffice.org-impress
    ```

2. Install UNO python library

    ```
    $ sudo apt-get install python-uno unoconv
    ```

3. Install necessary fonts (Especially for international language)

    ```
    Copy fonts to /usr/share/fonts/truetype/
    ```

    Then run

    ```
    $ fc-cache
    ```

4. Run OpenOffice as a service

    ```
    $ soffice -headless -nofirststartwizard -accept="socket,host=localhost,port=8100;urp;StarOffice.Service"
    ```

5. Convert document to PDF using unoconv command

    ```
    $ unoconv -f pdf __[filename]__
    ```

6. Create PDF thumbnail by using MuPDF tool

    ```
    $ pdfdraw -r 100 -o __[output-thumbnail]__ __[pdf-file]__ 1
    ```

http://www.artofsolving.com/opensource/pyodconverter
http://drbacchus.com/openoffice-python-uno-interface
bugs.debian.org/cgi-bin/bugreport.cgi?bug=491456


ffmpeg -i vid1.mp4 -vcodec mjpeg -vframes 1 -an -f rawvideo test.jpg