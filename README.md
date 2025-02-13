# pilot bloks demo API

Use the following endpoints to check and toggle a light’s pin state.

## Endpoints

1. **Check Pin State**  
   ```
   curl "http://[address]/status?pin=dio1"
   ```
   - Returns `"0"` if off, `"1"` if on.

2. **Turn On**  
   ```
   curl "http://[address]/on?pin=dio1"
   ```
   - Returns `"OK"` on success.

3. **Turn Off**  
   ```
   curl "http://[address]/off?pin=dio1"
   ```
   - Returns `"OK"` on success.

> **Note**: Replace `[address]` with server ip or domain
