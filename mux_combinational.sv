module Combinational_MUX
  #(parameter COO_EDGES = 6,
    parameter COO_BW = $clog2(COO_EDGES))
(
    input logic Selection,
    input logic [COO_BW-1:0] Instance0,
    input logic [COO_BW-1:0] Instance1,

    output logic [COO_BW-1:0] Outputt
);
  always_comb begin 
    case ( Selection )
      0 : Outputt = Instance0;
      1 : Outputt = Instance1;
  endcase
  end

endmodule
