module CounterFeature
#(parameter FEATURE_ROWS = 6,
    parameter COUNTER_FEATURE_WIDTH = $clog2(FEATURE_ROWS))
(
  input logic reset,
  input logic Feature_Enable,
  input logic clk,
  input logic [COUNTER_FEATURE_WIDTH-1:0] CountIn,

  output logic [COUNTER_FEATURE_WIDTH-1:0] count
);
 always_ff @(posedge reset or posedge clk)
    if (reset) begin 
        count <= 0;
	end
    else if (Feature_Enable) begin 
       if (count == FEATURE_ROWS-1) begin
	count <=0;
	end 
    else begin 
        count <= CountIn +1;
	end
 end
endmodule

