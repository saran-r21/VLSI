module Transformation_MUX
  #(parameter ADDRESS = 12)(
    input logic Selection,
    input logic [ADDRESS-1:0] Instance0,
    input logic [ADDRESS-1:0] Instance1,

    output logic [ADDRESS-1:0] Outputt
);
  always_comb begin
    case (Selection)
      0 : Outputt = Instance0;
      1 : Outputt = Instance1;
    endcase
  end

endmodule