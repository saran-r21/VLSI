module ArgmaxCombi
#(parameter COO_EDGES = 6,
    parameter COO_BW = $clog2(COO_EDGES),
    parameter DOT_PROD_WIDTH = 16,
    parameter WEIGHT_COLS = 3,
    parameter MAX_ADDRESS_WIDTH = 2)
(
  input logic comb_done,
  input logic reset,
  input logic clk,
  input logic [DOT_PROD_WIDTH-1:0] FM_WM_ADJ_ROW [0:2],

  output logic [MAX_ADDRESS_WIDTH-1:0]count
);
  always_comb begin
    if(FM_WM_ADJ_ROW[0]>=FM_WM_ADJ_ROW[1]) begin

        if(FM_WM_ADJ_ROW[0] >= FM_WM_ADJ_ROW[2])
            count=2'b00;
        else
            count=2'b10;
    end
    else
        
        if(FM_WM_ADJ_ROW[1] >= FM_WM_ADJ_ROW[2]) 
            count=2'b01;
        else
            count=2'b10;
        end
endmodule

