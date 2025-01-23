# agents/trip_planner.py

from typing import Dict, Any
import asyncio
from pymongo import MongoClient
from core.agent_base import BaseAgent
import openai
import os

class TripPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("TripPlanner")
        self.mongo_client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
        self.db = self.mongo_client.fursat
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Extract tour ID and customization requirements
            tour_id = message.get("tour_id")
            customization_needs = message.get("customization_needs", {})
            
            # Fetch base package data
            base_package = await self._fetch_package_data(tour_id)
            
            if not base_package:
                return {"error": "Package not found"}
            
            # Generate customized package
            customized_package = await self._customize_package(
                base_package,
                customization_needs
            )
            
            # Save customized package
            saved_package = await self._save_customized_package(customized_package)
            
            return {
                "status": "success",
                "package_id": saved_package["_id"],
                "package_url": f"https://fursat.fun/tours/{saved_package['_id']}"
            }
            
        except Exception as e:
            self.logger.error(f"Error processing trip plan: {str(e)}")
            return {"error": str(e)}

    async def _fetch_package_data(self, tour_id: str) -> Dict[str, Any]:
        """Fetch package data from MongoDB."""
        try:
            return self.db.tours.find_one({"_id": tour_id})
        except Exception as e:
            self.logger.error(f"Error fetching package: {str(e)}")
            raise

    async def _customize_package(
        self,
        base_package: Dict[str, Any],
        customization_needs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize package based on user needs using GPT."""
        try:
            # Prepare prompt for GPT
            prompt = self._prepare_customization_prompt(
                base_package,
                customization_needs
            )
            
            # Get customization suggestions from GPT
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a travel expert customizing tour packages."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse GPT response and modify package
            modifications = self._parse_gpt_response(response.choices[0].message.content)
            
            # Create new customized package
            customized_package = base_package.copy()
            customized_package.update(modifications)
            customized_package["is_customized"] = True
            customized_package["original_package_id"] = base_package["_id"]
            
            return customized_package
            
        except Exception as e:
            self.logger.error(f"Error customizing package: {str(e)}")
            raise

    def _prepare_customization_prompt(
        self,
        base_package: Dict[str, Any],
        customization_needs: Dict[str, Any]
    ) -> str:
        """Prepare prompt for GPT to customize package."""
        return f"""
        Base Package Details:
        - Destination: {base_package['destination']}
        - Duration: {base_package['duration']}
        - Activities: {', '.join(base_package['activities'])}
        
        Customer Customization Needs:
        {customization_needs}
        
        Please suggest modifications to this package considering the customer's needs.
        Return the response in a structured format that can be parsed into a package modification.
        """

    async def _save_customized_package(self, package: Dict[str, Any]) -> Dict[str, Any]:
        """Save customized package to MongoDB."""
        try:
            result = await self.db.customized_tours.insert_one(package)
            package["_id"] = result.inserted_id
            return package
        except Exception as e:
            self.logger.error(f"Error saving customized package: {str(e)}")
            raise