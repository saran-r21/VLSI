module VectMultiplier
#(
    // Parameters defining the widths and dimensions
    parameter FEATURE_WIDTH = 5,
    parameter WEIGHT_WIDTH = 5,
    parameter DOT_PROD_WIDTH = 16,
    parameter FEATURE_COLS = 96,
    parameter WEIGHT_ROWS = 96
)
(
    // Input feature column and weight row vectors
    input  [FEATURE_WIDTH-1 : 0] FEATURE_COL [0:FEATURE_COLS-1] ,
    input  [WEIGHT_WIDTH-1 : 0] WEIGHT_ROW [0: WEIGHT_ROWS-1],
    
    // Output dot product result
    output logic [DOT_PROD_WIDTH-1 : 0] PRODUCT
);
    // Intermediate registers to store partial results
    reg [DOT_PROD_WIDTH-1 : 0] Tempo [0: FEATURE_COLS-1];
    reg [DOT_PROD_WIDTH-1 : 0] S1 [0: 47];
    reg [DOT_PROD_WIDTH-1 : 0] S2 [0: 23];
    reg [DOT_PROD_WIDTH-1 : 0] S3 [0: 11];
    reg [DOT_PROD_WIDTH-1 : 0] S4 [0: 5];
    reg [DOT_PROD_WIDTH-1 : 0] S5 [0: 3];

    always_comb  
    begin 
        // Calculate the product of each element in FEATURE_COL and WEIGHT_ROW
        for (int a=0; a<96; a++) begin
            Tempo[a] = FEATURE_COL[a] * WEIGHT_ROW[a];
        end
        
        // Perform a binary tree sum to accumulate partial products
        for (int b=47; b>=0; b--) begin
            S1[b] = Tempo[b] + Tempo[b+48];
        end

        for (int c=23; c>=0; c--) begin
            S2[c] = S1[c] + S1[c+24];
        end

        for (int d=11; d>=0; d--) begin
            S3[d] = S2[d] + S2[d+12];
        end

        for (int e=5; e>=0; e--) begin
            S4[e] = S3[e] + S3[e+6];
        end

        for (int f=2; f>=0; f--) begin
            S5[f] = S4[f] + S4[f+3];
        end

        // Final dot product result
        PRODUCT = S5[0] + S5[1] + S5[2];
    end
endmodule

