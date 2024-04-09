module CounterEdge
#(
    // Total number of edges to count
    parameter COO_EDGES = 6,
    
    // Bitwidth for representing the count
    parameter COO_BW = $clog2(COO_EDGES)
)
(
    // Asynchronous reset signal
    input logic reset,
    
    // Signal to enable counting edges
    input logic Edge_Enable,
    
    // Clock input
    input logic clk,
    
    // Input count value
    input logic [COO_BW-1:0] CountIn,

    // Output count value
    output logic [COO_BW-1:0] count
);
    // Always block for sequential logic
    always_ff @(posedge reset or posedge clk)
        if (reset) begin
            // Reset the count to 0
            count <= 0;
        end
        else if (Edge_Enable) begin
            // Check if the count is at its maximum value
            if (count == COO_EDGES - 1) begin
                // Reset the count to 0 if it reaches the maximum
                count <= 0;
            end
            else begin
                // Increment the count by 1
                count <= CountIn + 1;
            end
        end
endmodule

