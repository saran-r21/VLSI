module CounterWeight
#(parameter WEIGHT_COLS = 3,
    parameter COUNTER_WEIGHT_WIDTH = $clog2(WEIGHT_COLS))
(
  input logic reset,
  input logic Weight_Enable,
  input logic clk,
  input logic [COUNTER_WEIGHT_WIDTH-1:0] CountIn,

  output logic [COUNTER_WEIGHT_WIDTH-1:0] count
);
 always_ff @(posedge reset or posedge clk)
    if (reset) begin
        count <= 0;
    end
    else if (Weight_Enable) begin
	if(count == WEIGHT_COLS-1) begin
	  count<=0;
	end
        else begin
        count <= CountIn +1;
    	end
     end
endmodule