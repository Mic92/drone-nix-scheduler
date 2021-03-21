{
  description = "Schedule jobs from hydra-eval-jobs as drone builds";

  inputs.hydra-eval-jobs.url = "github:Mic92/hydra-eval-jobs";
  inputs.hydra-eval-jobs.inputs.nixpkgs.follows = "nixpkgs";
  inputs.hydra-eval-jobs.inputs.flake-utils.follows = "flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils, hydra-eval-jobs }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      rec {
        packages = {
          drone-nix-scheduler = pkgs.callPackage ./default.nix {
            srcDir = self;
          };
          inherit (hydra-eval-jobs.packages.${system}) hydra-eval-jobs;
        };
        defaultPackage = self.packages.${system}.drone-nix-scheduler;
      });
}
