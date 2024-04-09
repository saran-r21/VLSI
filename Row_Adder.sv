module RowAdder
#(
  // Parameters defining the dimensions and widths of matrices
  parameter FEATURE_ROWS = 6,
  parameter WEIGHT_COLS = 3,
  parameter DOT_PROD_WIDTH = 16,
  parameter ADDRESS_WIDTH = 13,
  parameter WEIGHT_WIDTH = $clog2(WEIGHT_COLS),
  parameter FEATURE_WIDTH = $clog2(FEATURE_ROWS)
)
(
  // Input values for addition
  input logic [DOT_PROD_WIDTH - 1:0] Value1 [0:WEIGHT_COLS-1],
  input logic [DOT_PROD_WIDTH - 1:0] Value2 [0:WEIGHT_COLS-1],

  // Output sum values
  output logic [DOT_PROD_WIDTH - 1:0] FM_WM_Output [0:WEIGHT_COLS-1]
);

  // Combinational logic to perform element-wise addition
  always_comb begin
    FM_WM_Output[0] <= Value1[0] + Value2[0];
    FM_WM_Output[1] <= Value1[1] + Value2[1];
    FM_WM_Output[2] <= Value1[2] + Value2[2];
  end
endmodule

