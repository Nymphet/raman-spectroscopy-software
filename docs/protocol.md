
# Commands

the controller of the CCD is assumed to accpet the following basic commands:

    #Start%       Start collecting and sending data
    #Stop%        Stop collecting and sending data
    #Onestep%     Collect and send data once
    #IT:???ms%    Set CCD integration time to ??? ms
    #IT:???ss%    Set CCD integration time to ??? s

## Detailed Explainations

### #Start%

On receiving this command, the CCD controller starts to collect data immediately.
If the integration time is greater than 100 ms, the CCD will send a total of 3694 unsigned short integer type little-endian data (3694*2 8bit) to the host computer immediately after the data is collected. The data represents light intensities on each of the pixels of the linear CCD.
When the integration time is less than 100 ms, the frame rate of the uploading will be 10 frames per second.

### #Stop%

On receiving this command, the CCD controller stops collecting and sending data to the host computer.

### #Onestep%

The CCD controller collects one set of data immediately and send it to the host computer. Then it stops collecting data, regardless of whether it is collecting data before this command is received.

### #IT:???ms%

Change the integration time internal setting of the CCD controller to ??? ms. For example, the commad #IT:500ms% sets the integration time of the CCD to 500 ms.

### #IT:???ss%

Change the integration time internal setting of the CCD controller to ??? s. For example, the commad #IT:010ss% sets the integration time of the CCD to 10 seconds.