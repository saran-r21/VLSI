module Matrix_argmax_Memory 
  #(parameter FEATURE_ROWS = 6,
    parameter WEIGHT_COLS = 3,
    parameter DOT_PROD_WIDTH = 16,
    parameter WEIGHT_WIDTH = $clog2(WEIGHT_COLS),
    parameter FEATURE_WIDTH = $clog2(FEATURE_ROWS)
)
(
    input logic clk,
    input logic rst,
    input logic [FEATURE_WIDTH-1:0] write_row,
    input logic read,
    input logic wr_en,
    input logic [WEIGHT_WIDTH - 1:0] fm_wm_adj_row_in,
    output logic [WEIGHT_WIDTH - 1:0] fm_wm_adj_out [0:FEATURE_ROWS-1]
);

    
    // Declare memory array to store matrix data
    logic [WEIGHT_WIDTH - 1:0] mem  [0:FEATURE_ROWS-1];

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            // Reset memory to 0 on reset
	    
		for (int j = 0; j < FEATURE_ROWS; j = j + 1) begin
          	    mem [j] <= '0;
 		end 
        
        end else if (wr_en) begin
            // Write data to memory at the specified row
            mem[write_row] <= fm_wm_adj_row_in;

        end
    end

    assign fm_wm_adj_out = mem;
endmodule