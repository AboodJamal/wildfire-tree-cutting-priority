"""
Fire Creek Tree Cutting Priority Analysis - Using Real Data
============================================================

This script analyzes the actual Fire Creek data to determine tree cutting priority
based on five factors:
    1. Tree Mortality (SBNFMortalityt)
    2. Community Features (Communityfeatures)
    3. Egress Routes (EgressRoutes)
    4. Populated Areas (PopulatedAreast)
    5. Electric Utilities (Transmission, SubTransmission, DistCircuits, Substations, PoleTopSubs)

Author: Spatial Data Analysis Project
Date: December 2025
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import warnings

warnings.filterwarnings("ignore")


class FireCreekAnalysis:
    """Main analysis class for Fire Creek tree cutting priority."""

    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Data layers
        self.cutting_grid = None
        self.tree_mortality = None
        self.community_features = None
        self.egress_routes = None
        self.populated_areas = None

        # Electric utilities
        self.transmission = None
        self.sub_transmission = None
        self.dist_circuits = None
        self.substations = None
        self.pole_top_subs = None

        # Results
        self.results = None

        # Weights for each factor (must sum to 1.0)
        self.weights = {
            "tree_mortality": 0.25,
            "community_features": 0.20,
            "egress_routes": 0.20,
            "populated_areas": 0.20,
            "electric_utilities": 0.15,
        }

    def load_data(self):
        """Load all shapefiles."""
        print("\n" + "=" * 70)
        print("LOADING SPATIAL DATA")
        print("=" * 70)

        try:
            # Load cutting grid
            self.cutting_grid = gpd.read_file(
                os.path.join(self.data_dir, "CuttingGrids.shp")
            )
            print(f"✓ Cutting Grid: {len(self.cutting_grid)} cells loaded")

            # Load tree mortality
            self.tree_mortality = gpd.read_file(
                os.path.join(self.data_dir, "SBNFMortalityt.shp")
            )
            print(f"✓ Tree Mortality: {len(self.tree_mortality)} features loaded")

            # Load community features
            self.community_features = gpd.read_file(
                os.path.join(self.data_dir, "Communityfeatures.shp")
            )
            print(
                f"✓ Community Features: {len(self.community_features)} features loaded"
            )

            # Load egress routes
            self.egress_routes = gpd.read_file(
                os.path.join(self.data_dir, "EgressRoutes.shp")
            )
            print(f"✓ Egress Routes: {len(self.egress_routes)} routes loaded")

            # Load populated areas
            self.populated_areas = gpd.read_file(
                os.path.join(self.data_dir, "PopulatedAreast.shp")
            )
            print(f"✓ Populated Areas: {len(self.populated_areas)} areas loaded")

            # Load electric utilities
            self.transmission = gpd.read_file(
                os.path.join(self.data_dir, "Transmission.shp")
            )
            print(f"✓ Transmission Lines: {len(self.transmission)} lines loaded")

            self.sub_transmission = gpd.read_file(
                os.path.join(self.data_dir, "SubTransmission.shp")
            )
            print(
                f"✓ Sub-Transmission Lines: {len(self.sub_transmission)} lines loaded"
            )

            self.dist_circuits = gpd.read_file(
                os.path.join(self.data_dir, "DistCircuits.shp")
            )
            print(f"✓ Distribution Circuits: {len(self.dist_circuits)} circuits loaded")

            self.substations = gpd.read_file(
                os.path.join(self.data_dir, "Substations.shp")
            )
            print(f"✓ Substations: {len(self.substations)} substations loaded")

            self.pole_top_subs = gpd.read_file(
                os.path.join(self.data_dir, "PoleTopSubs.shp")
            )
            print(f"✓ Pole-Top Substations: {len(self.pole_top_subs)} units loaded")

            # Ensure all layers have the same CRS
            self._reproject_layers()

            print("\n✓ All data loaded successfully!")

        except Exception as e:
            print(f"✗ Error loading data: {e}")
            raise

    def _reproject_layers(self):
        """Ensure all layers use the same coordinate reference system."""
        base_crs = self.cutting_grid.crs

        layers = [
            ("tree_mortality", self.tree_mortality),
            ("community_features", self.community_features),
            ("egress_routes", self.egress_routes),
            ("populated_areas", self.populated_areas),
            ("transmission", self.transmission),
            ("sub_transmission", self.sub_transmission),
            ("dist_circuits", self.dist_circuits),
            ("substations", self.substations),
            ("pole_top_subs", self.pole_top_subs),
        ]

        for name, layer in layers:
            if layer.crs != base_crs:
                layer = layer.to_crs(base_crs)
                setattr(self, name, layer)
                print(f"  Reprojected {name} to {base_crs}")

    def _normalize_score(self, values, inverse=False):
        """Normalize values to 0-10 scale."""
        values = np.array(values, dtype=float)

        if len(values) == 0 or np.all(np.isnan(values)):
            return np.zeros(len(values))

        min_val = np.nanmin(values)
        max_val = np.nanmax(values)

        if max_val == min_val:
            return np.full(len(values), 5.0)

        if inverse:
            normalized = 10 - (values - min_val) / (max_val - min_val) * 10
        else:
            normalized = (values - min_val) / (max_val - min_val) * 10

        return normalized

    def calculate_tree_mortality_score(self):
        """Calculate tree mortality score for each grid cell."""
        print("\n" + "=" * 70)
        print("FACTOR 1: TREE MORTALITY SCORE")
        print("=" * 70)

        scores = []

        for idx, grid_cell in self.cutting_grid.iterrows():
            # Find overlapping mortality areas
            overlaps = self.tree_mortality[
                self.tree_mortality.geometry.intersects(grid_cell.geometry)
            ]

            if len(overlaps) > 0:
                # Calculate area-weighted mortality
                total_intersection_area = 0
                weighted_mortality = 0

                for _, mortality_area in overlaps.iterrows():
                    intersection = grid_cell.geometry.intersection(
                        mortality_area.geometry
                    )
                    intersection_area = intersection.area

                    # Check for mortality value in different possible column names
                    mortality_value = 0
                    for col in mortality_area.index:
                        if (
                            "mort" in col.lower()
                            or "value" in col.lower()
                            or "rate" in col.lower()
                        ):
                            try:
                                mortality_value = float(mortality_area[col])
                                break
                            except:
                                continue

                    weighted_mortality += mortality_value * intersection_area
                    total_intersection_area += intersection_area

                if total_intersection_area > 0:
                    score = weighted_mortality / total_intersection_area
                else:
                    score = 0
            else:
                score = 0

            scores.append(score)

        self.cutting_grid["mortality_score"] = scores
        self.cutting_grid["mortality_score_norm"] = self._normalize_score(scores)

        print(f"✓ Mortality scores calculated")
        print(f"  Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Cells with mortality: {sum(1 for s in scores if s > 0)}")

    def calculate_community_score(self):
        """Calculate community features proximity score."""
        print("\n" + "=" * 70)
        print("FACTOR 2: COMMUNITY FEATURES SCORE")
        print("=" * 70)

        scores = []

        for idx, grid_cell in self.cutting_grid.iterrows():
            max_score = 0

            for _, feature in self.community_features.iterrows():
                distance = grid_cell.geometry.distance(feature.geometry)

                # Get importance weight if available
                importance = 10  # Default high importance
                for col in feature.index:
                    if (
                        "import" in col.lower()
                        or "prior" in col.lower()
                        or "weight" in col.lower()
                    ):
                        try:
                            importance = float(feature[col])
                            break
                        except:
                            continue

                # Distance-based scoring
                if distance == 0 or grid_cell.geometry.intersects(feature.geometry):
                    score = importance
                elif distance < 100:  # Within 100 meters
                    score = importance * (1 - distance / 100)
                elif distance < 300:  # Within 300 meters
                    score = importance * 0.5 * (1 - (distance - 100) / 200)
                else:
                    score = 0

                max_score = max(max_score, score)

            scores.append(max_score)

        self.cutting_grid["community_score"] = scores
        self.cutting_grid["community_score_norm"] = self._normalize_score(scores)

        print(f"✓ Community scores calculated")
        print(f"  Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Cells near features: {sum(1 for s in scores if s > 0)}")

    def calculate_egress_score(self):
        """Calculate egress routes proximity score."""
        print("\n" + "=" * 70)
        print("FACTOR 3: EGRESS ROUTES SCORE")
        print("=" * 70)

        scores = []

        for idx, grid_cell in self.cutting_grid.iterrows():
            max_score = 0

            for _, route in self.egress_routes.iterrows():
                distance = grid_cell.geometry.distance(route.geometry)

                # Get route priority if available
                priority = 10  # Default high priority
                for col in route.index:
                    if (
                        "prior" in col.lower()
                        or "import" in col.lower()
                        or "class" in col.lower()
                    ):
                        try:
                            priority = float(route[col])
                            break
                        except:
                            continue

                # Distance-based scoring (routes need wider buffer)
                if distance == 0 or grid_cell.geometry.intersects(route.geometry):
                    score = priority
                elif distance < 50:  # Within 50 meters (tree fall distance)
                    score = priority * (1 - distance / 50)
                elif distance < 150:  # Extended buffer
                    score = priority * 0.5 * (1 - (distance - 50) / 100)
                else:
                    score = 0

                max_score = max(max_score, score)

            scores.append(max_score)

        self.cutting_grid["egress_score"] = scores
        self.cutting_grid["egress_score_norm"] = self._normalize_score(scores)

        print(f"✓ Egress scores calculated")
        print(f"  Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Cells near routes: {sum(1 for s in scores if s > 0)}")

    def calculate_population_score(self):
        """Calculate populated areas score."""
        print("\n" + "=" * 70)
        print("FACTOR 4: POPULATED AREAS SCORE")
        print("=" * 70)

        scores = []

        for idx, grid_cell in self.cutting_grid.iterrows():
            total_score = 0

            for _, area in self.populated_areas.iterrows():
                if grid_cell.geometry.intersects(area.geometry):
                    intersection = grid_cell.geometry.intersection(area.geometry)
                    ratio = intersection.area / grid_cell.geometry.area

                    # Get population density if available
                    pop_density = 10  # Default high density
                    for col in area.index:
                        if (
                            "pop" in col.lower()
                            or "dens" in col.lower()
                            or "people" in col.lower()
                        ):
                            try:
                                pop_density = float(area[col])
                                break
                            except:
                                continue

                    total_score += ratio * pop_density

            scores.append(total_score)

        self.cutting_grid["population_score"] = scores
        self.cutting_grid["population_score_norm"] = self._normalize_score(scores)

        print(f"✓ Population scores calculated")
        print(f"  Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Cells in populated areas: {sum(1 for s in scores if s > 0)}")

    def calculate_utility_score(self):
        """Calculate electric utilities proximity score."""
        print("\n" + "=" * 70)
        print("FACTOR 5: ELECTRIC UTILITIES SCORE")
        print("=" * 70)

        scores = []

        # Combine all utility layers with different priorities
        utility_layers = [
            (self.transmission, 10, "Transmission"),
            (self.sub_transmission, 8, "Sub-Transmission"),
            (self.dist_circuits, 6, "Distribution"),
            (self.substations, 10, "Substations"),
            (self.pole_top_subs, 7, "Pole-Top Subs"),
        ]

        for idx, grid_cell in self.cutting_grid.iterrows():
            max_score = 0

            for utility_layer, base_priority, name in utility_layers:
                for _, utility in utility_layer.iterrows():
                    distance = grid_cell.geometry.distance(utility.geometry)

                    # Distance-based scoring (utilities need buffer zones)
                    if distance == 0 or grid_cell.geometry.intersects(utility.geometry):
                        score = base_priority
                    elif distance < 30:  # Within 30 meters (tree fall zone)
                        score = base_priority * (1 - distance / 30)
                    elif distance < 100:  # Extended buffer
                        score = base_priority * 0.5 * (1 - (distance - 30) / 70)
                    else:
                        score = 0

                    max_score = max(max_score, score)

            scores.append(max_score)

        self.cutting_grid["utility_score"] = scores
        self.cutting_grid["utility_score_norm"] = self._normalize_score(scores)

        print(f"✓ Utility scores calculated")
        print(f"  Range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"  Mean: {np.mean(scores):.2f}")
        print(f"  Cells near utilities: {sum(1 for s in scores if s > 0)}")

    def calculate_overall_priority(self):
        """Calculate overall tree cutting priority."""
        print("\n" + "=" * 70)
        print("CALCULATING OVERALL PRIORITY")
        print("=" * 70)

        print("\nWeights applied:")
        for factor, weight in self.weights.items():
            print(f"  {factor.replace('_', ' ').title()}: {weight*100:.0f}%")

        # Calculate weighted sum
        self.cutting_grid["overall_priority"] = (
            self.cutting_grid["mortality_score_norm"] * self.weights["tree_mortality"]
            + self.cutting_grid["community_score_norm"]
            * self.weights["community_features"]
            + self.cutting_grid["egress_score_norm"] * self.weights["egress_routes"]
            + self.cutting_grid["population_score_norm"]
            * self.weights["populated_areas"]
            + self.cutting_grid["utility_score_norm"]
            * self.weights["electric_utilities"]
        )

        # Normalize to 0-10 scale
        self.cutting_grid["priority_normalized"] = self._normalize_score(
            self.cutting_grid["overall_priority"]
        )

        # Classify into priority levels
        self.cutting_grid["priority_class"] = pd.cut(
            self.cutting_grid["priority_normalized"],
            bins=[0, 2, 4, 6, 8, 10],
            labels=["Very Low", "Low", "Medium", "High", "Very High"],
            include_lowest=True,
        )

        # Rank cells
        self.cutting_grid["priority_rank"] = (
            self.cutting_grid["priority_normalized"]
            .rank(ascending=False, method="dense")
            .astype(int)
        )

        # Results
        self.results = self.cutting_grid.copy()

        print("\nPriority Distribution:")
        for priority in ["Very High", "High", "Medium", "Low", "Very Low"]:
            count = (self.cutting_grid["priority_class"] == priority).sum()
            pct = count / len(self.cutting_grid) * 100
            print(f"  {priority:12}: {count:4} cells ({pct:5.1f}%)")

        print(f"\n✓ Overall priority calculated for {len(self.cutting_grid)} cells")

    def save_results(self):
        """Save results to files."""
        print("\n" + "=" * 70)
        print("SAVING RESULTS")
        print("=" * 70)

        # Save as shapefile
        output_shp = os.path.join(self.output_dir, "TreeCuttingPriority.shp")
        self.results.to_file(output_shp)
        print(f"✓ Shapefile saved: {output_shp}")

        # Save as GeoJSON
        output_geojson = os.path.join(self.output_dir, "TreeCuttingPriority.geojson")
        self.results.to_file(output_geojson, driver="GeoJSON")
        print(f"✓ GeoJSON saved: {output_geojson}")

        # Save summary CSV
        summary_cols = [
            "mortality_score_norm",
            "community_score_norm",
            "egress_score_norm",
            "population_score_norm",
            "utility_score_norm",
            "priority_normalized",
            "priority_class",
            "priority_rank",
        ]
        summary_df = self.results[summary_cols].copy()
        summary_path = os.path.join(self.output_dir, "priority_summary.csv")
        summary_df.to_csv(summary_path, index=False)
        print(f"✓ Summary CSV saved: {summary_path}")

        # Save high priority areas only
        high_priority = self.results[
            self.results["priority_class"].isin(["Very High", "High"])
        ].copy()
        high_priority_path = os.path.join(self.output_dir, "HighPriorityCells.shp")
        high_priority.to_file(high_priority_path)
        print(f"✓ High priority cells saved: {high_priority_path}")

    def create_maps(self):
        """Create visualization maps."""
        print("\n" + "=" * 70)
        print("CREATING MAPS")
        print("=" * 70)

        # Create priority color map
        colors = ["#1a9850", "#91cf60", "#fee08b", "#fc8d59", "#d73027"]
        cmap = LinearSegmentedColormap.from_list("priority", colors, N=256)

        # Map 1: Overall Priority
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))
        self.results.plot(
            column="priority_normalized",
            ax=ax,
            cmap=cmap,
            legend=True,
            legend_kwds={"label": "Priority Score (0-10)", "shrink": 0.8},
        )
        ax.set_title(
            "Fire Creek Tree Cutting Priority Map", fontsize=16, fontweight="bold"
        )
        ax.set_xlabel("X Coordinate", fontsize=12)
        ax.set_ylabel("Y Coordinate", fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        map_path = os.path.join(self.output_dir, "priority_map.png")
        plt.savefig(map_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Priority map saved: {map_path}")

        # Map 2: Priority Classes
        fig, ax = plt.subplots(1, 1, figsize=(14, 12))

        class_colors = {
            "Very Low": "#1a9850",
            "Low": "#91cf60",
            "Medium": "#fee08b",
            "High": "#fc8d59",
            "Very High": "#d73027",
        }

        for priority_class, color in class_colors.items():
            subset = self.results[self.results["priority_class"] == priority_class]
            if len(subset) > 0:
                subset.plot(ax=ax, color=color, edgecolor="gray", linewidth=0.1)

        patches = [
            mpatches.Patch(color=color, label=label)
            for label, color in class_colors.items()
        ]
        ax.legend(handles=patches, loc="upper right", title="Priority Class")

        ax.set_title(
            "Fire Creek Tree Cutting Priority Classes", fontsize=16, fontweight="bold"
        )
        ax.set_xlabel("X Coordinate", fontsize=12)
        ax.set_ylabel("Y Coordinate", fontsize=12)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        class_map_path = os.path.join(self.output_dir, "priority_classes_map.png")
        plt.savefig(class_map_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Priority classes map saved: {class_map_path}")

        # Map 3: Factor Maps
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()

        factors = [
            ("mortality_score_norm", "Tree Mortality"),
            ("community_score_norm", "Community Features"),
            ("egress_score_norm", "Egress Routes"),
            ("population_score_norm", "Populated Areas"),
            ("utility_score_norm", "Electric Utilities"),
            ("priority_normalized", "Overall Priority"),
        ]

        for i, (col, title) in enumerate(factors):
            self.results.plot(
                column=col,
                ax=axes[i],
                cmap=cmap,
                legend=True,
                legend_kwds={"shrink": 0.6},
            )
            axes[i].set_title(title, fontsize=11, fontweight="bold")
            axes[i].grid(True, alpha=0.2)

        plt.suptitle(
            "Fire Creek Tree Cutting Priority - Factor Analysis",
            fontsize=14,
            fontweight="bold",
        )
        plt.tight_layout()

        factor_map_path = os.path.join(self.output_dir, "factor_maps.png")
        plt.savefig(factor_map_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Factor maps saved: {factor_map_path}")

    def generate_report(self):
        """Generate analysis report."""
        print("\n" + "=" * 70)
        print("GENERATING REPORT")
        print("=" * 70)

        report = []
        report.append("=" * 70)
        report.append("FIRE CREEK TREE CUTTING PRIORITY ANALYSIS - REPORT")
        report.append("=" * 70)

        report.append("\n1. STUDY AREA")
        report.append("-" * 40)
        report.append(f"Total grid cells analyzed: {len(self.results)}")

        report.append("\n2. WEIGHTS APPLIED")
        report.append("-" * 40)
        for factor, weight in self.weights.items():
            report.append(f"{factor.replace('_', ' ').title():25}: {weight*100:.0f}%")

        report.append("\n3. PRIORITY DISTRIBUTION")
        report.append("-" * 40)
        for priority in ["Very High", "High", "Medium", "Low", "Very Low"]:
            count = (self.results["priority_class"] == priority).sum()
            pct = count / len(self.results) * 100
            report.append(f"{priority:12}: {count:5} cells ({pct:6.2f}%)")

        report.append("\n4. TOP 10 HIGHEST PRIORITY CELLS")
        report.append("-" * 40)
        top_10 = self.results.nsmallest(10, "priority_rank")
        for _, row in top_10.iterrows():
            centroid = row.geometry.centroid
            report.append(
                f"Rank {int(row['priority_rank']):4} | "
                f"Score: {row['priority_normalized']:.2f} | "
                f"Class: {row['priority_class']}"
            )

        report.append("\n5. RECOMMENDATIONS")
        report.append("-" * 40)
        very_high = (self.results["priority_class"] == "Very High").sum()
        high = (self.results["priority_class"] == "High").sum()
        report.append(f"• {very_high} cells require IMMEDIATE attention")
        report.append(f"• {high} cells should be addressed soon")
        report.append("• Focus on:")
        report.append("  - Areas with high tree mortality")
        report.append("  - Cells near community facilities")
        report.append("  - Zones along evacuation routes")
        report.append("  - High population density areas")
        report.append("  - Critical utility infrastructure")

        report.append("\n" + "=" * 70)

        report_text = "\n".join(report)
        print(report_text)

        # Save report
        report_path = os.path.join(self.output_dir, "analysis_report.txt")
        with open(report_path, "w") as f:
            f.write(report_text)
        print(f"\n✓ Report saved: {report_path}")

    def run_analysis(self):
        """Run the complete analysis."""
        print("\n" + "=" * 70)
        print("FIRE CREEK TREE CUTTING PRIORITY ANALYSIS")
        print("=" * 70)

        self.load_data()

        self.calculate_tree_mortality_score()
        self.calculate_community_score()
        self.calculate_egress_score()
        self.calculate_population_score()
        self.calculate_utility_score()

        self.calculate_overall_priority()

        self.save_results()
        self.create_maps()
        self.generate_report()

        print("\n" + "=" * 70)
        print("ANALYSIS COMPLETE!")
        print("=" * 70)
        print(f"\nAll results saved to: {self.output_dir}")


if __name__ == "__main__":
    # Set directories
    project_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(project_dir, "data")
    output_dir = os.path.join(project_dir, "output")

    # Run analysis
    analysis = FireCreekAnalysis(data_dir, output_dir)
    analysis.run_analysis()
